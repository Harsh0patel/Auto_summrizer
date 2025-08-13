import pandas as pd
import sentencepiece as spm
import os
import ast
import torch
from torch import nn
from torch.nn import Embedding, LSTM
from torch.utils.data import DataLoader, Dataset
from torch.nn.utils.rnn import pad_sequence
import gc

# Encoder class
class Encoderlstm(torch.nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_size):
        super().__init__()
        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embedding_dim)
        self.lstm = nn.LSTM(input_size=embedding_dim, hidden_size=hidden_size, batch_first=True)

    def forward(self, input_ids):
        x = self.embedding(input_ids)
        outputs, (h, c) = self.lstm(x)
        return outputs, (h, c)

# Fixed Decoder class with memory-efficient attention
class DecoderLSTM(torch.nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_size):
        super().__init__()
        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embedding_dim)
        self.lstm = nn.LSTM(input_size=embedding_dim + hidden_size, hidden_size=hidden_size, batch_first=True)
        self.output_projection = nn.Linear(hidden_size, vocab_size)

        # Attention layers
        self.attention = nn.Linear(hidden_size * 2, hidden_size)
        self.context_projection = nn.Linear(hidden_size, hidden_size)

    def forward(self, input_token, hidden_state, encoder_outputs):
        # input_token: (batch_size, 1)
        # hidden_state: tuple of (h, c) where h,c are (1, batch_size, hidden_size)
        # encoder_outputs: (batch_size, src_len, hidden_size)

        batch_size = input_token.size(0)
        src_len = encoder_outputs.size(1)

        # Embed input token
        embedded = self.embedding(input_token)  # (batch_size, 1, embedding_dim)

        # Calculate attention weights more efficiently
        decoder_hidden = hidden_state[0].transpose(0, 1)  # (batch_size, 1, hidden_size)

        # Expand decoder hidden to match encoder outputs length
        decoder_hidden_expanded = decoder_hidden.expand(-1, src_len, -1)  # (batch_size, src_len, hidden_size)

        # Concatenate and compute attention
        combined = torch.cat([decoder_hidden_expanded, encoder_outputs], dim=2)  # (batch_size, src_len, hidden_size*2)
        energy = torch.tanh(self.attention(combined))  # (batch_size, src_len, hidden_size)

        # Attention weights
        attention_weights = torch.softmax(energy.sum(dim=2), dim=1)  # (batch_size, src_len)

        # Context vector
        context = torch.bmm(attention_weights.unsqueeze(1), encoder_outputs)  # (batch_size, 1, hidden_size)

        # Apply context projection to reduce dimension if needed
        context = self.context_projection(context)  # (batch_size, 1, hidden_size)

        # Combine embedding and context
        lstm_input = torch.cat([embedded, context], dim=2)  # (batch_size, 1, embedding_dim + hidden_size)

        # LSTM forward pass
        output, new_hidden = self.lstm(lstm_input, hidden_state)

        # Project to vocabulary
        logits = self.output_projection(output)  # (batch_size, 1, vocab_size)

        return logits, new_hidden

# Memory-efficient Trainer
class Trainer:
    def __init__(self, encoder, decoder, optimizer, loss_fn, device):
        self.encoder = encoder
        self.decoder = decoder
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.device = device

    def train(self, dataloader, epochs=5, teacher_forcing_ratio=0.5, checkpoint_path='/content/drive/MyDrive/Auto Summrizer/check_point/checkpoint.pth'):
        self.encoder.train()
        self.decoder.train()

        # Create the directory if it doesn't exist
        checkpoint_dir = os.path.dirname(checkpoint_path)
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)

        start_epoch = 0
        if os.path.exists(checkpoint_path):
            checkpoint = torch.load(checkpoint_path)
            self.encoder.load_state_dict(checkpoint['encoder_state_dict'])
            self.decoder.load_state_dict(checkpoint['decoder_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            start_epoch = checkpoint['epoch']
            print(f"Resuming training from epoch {start_epoch}")


        for epoch in range(start_epoch, epochs):
            total_loss = 0

            for batch_idx, batch in enumerate(dataloader):
                # Clear cache periodically
                if batch_idx % 10 == 0:
                    torch.cuda.empty_cache() if torch.cuda.is_available() else None
                    gc.collect()

                input_ids = batch["input_ids"].to(self.device)
                target_ids = batch["target_ids"].to(self.device)

                batch_size, tgt_len = target_ids.shape
                vocab_size = self.decoder.output_projection.out_features

                # Encode source
                encoder_outputs, encoder_hidden = self.encoder(input_ids)

                # Initialize decoder
                decoder_hidden = encoder_hidden
                decoder_input = target_ids[:, 0:1].to(self.device)  # (batch_size, 1) - start token

                total_loss_batch = 0

                # Decode step by step
                for t in range(1, tgt_len):
                    # Move decoder_hidden to the correct device if needed
                    decoder_hidden = (decoder_hidden[0].to(self.device), decoder_hidden[1].to(self.device))

                    # Forward pass
                    decoder_output, decoder_hidden = self.decoder(
                        decoder_input, decoder_hidden, encoder_outputs
                    )

                    # Get logits for current step
                    logits = decoder_output.squeeze(1)  # (batch_size, vocab_size)

                    # Calculate loss for current step
                    targets = target_ids[:, t]  # (batch_size,)
                    loss = self.loss_fn(logits, targets)
                    total_loss_batch += loss

                    # Teacher forcing
                    if torch.rand(1).item() < teacher_forcing_ratio:
                        decoder_input = target_ids[:, t:t+1].to(self.device)  # Use ground truth
                    else:
                        decoder_input = logits.argmax(dim=1, keepdim=True).to(self.device)  # Use prediction


                # Average loss across sequence length
                avg_loss = total_loss_batch / (tgt_len - 1)

                # Backward pass
                self.optimizer.zero_grad()
                avg_loss.backward()

                # Gradient clipping to prevent exploding gradients
                torch.nn.utils.clip_grad_norm_(
                    list(self.encoder.parameters()) + list(self.decoder.parameters()),
                    max_norm=1.0
                )

                self.optimizer.step()

                total_loss += avg_loss.item()

                # Clear variables
                del encoder_outputs, encoder_hidden, decoder_hidden
                torch.cuda.empty_cache() if torch.cuda.is_available() else None
                gc.collect()


                if batch_idx % 50 == 0:
                    print(f"Epoch {epoch+1}, Batch {batch_idx}, Loss: {avg_loss.item():.4f}")

            avg_epoch_loss = total_loss / len(dataloader)
            print(f"Epoch [{epoch+1}/{epochs}] Average Loss: {avg_epoch_loss:.4f}")

            # Save checkpoint
            checkpoint = {
                'epoch': epoch + 1,
                'encoder_state_dict': self.encoder.state_dict(),
                'decoder_state_dict': self.decoder.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
            }
            torch.save(checkpoint, checkpoint_path)
            print(f"Checkpoint saved to {checkpoint_path}")