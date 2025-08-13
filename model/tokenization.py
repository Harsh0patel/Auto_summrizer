import pandas as pd
import sentencepiece as spm

spm.SentencePieceTrainer.Train(input = ['train_data.csv'], model_prefix = 'bpe', vocab_size = 10000)
sp = spm.SentencePieceProcessor(model_file = 'bpe.model')
df1 = pd.read_json('data/clean_train_1.json')
df2 = pd.read_json('data/clean_train_2.json')
df3 = pd.read_json('data/test.json')

abstract_tokens_train = []  #500
text_tokens_train = []  #5000
text_tokens_test = []
abstract_tokens_test = []

for i in range(len(df1)):
    abstract_tokens_train.append(sp.encode(df1.at[i, 'cleaned_abstract']))
    text_tokens_train.append(sp.Encode(df1.at[i, 'cleaned_text']))

for i in range(len(df2)):
    abstract_tokens_train.append(sp.encode(df2.at[i, 'cleaned_abstract']))
    text_tokens_train.append(sp.encode(df2.at[i, 'cleaned_text']))

for i in range(len(df3)):
    text_tokens_test.append(sp.encode(df3.at[i, 'cleaned_article']))
    abstract_tokens_test.append(sp.encode(df3.at[i, 'cleaned_abstract']))

print(len(text_tokens_train), len(abstract_tokens_train), len(text_tokens_test), len(abstract_tokens_test))

df4 = pd.DataFrame({'abstract_tokens' : abstract_tokens_test, 'text_tokens': text_tokens_test})
df4.to_csv('test_tokens.csv', index = False)