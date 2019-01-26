'''
  code by Tae Hwan Jung(Jeff Jung) @graykode
'''
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable

dtype = torch.FloatTensor

char_arr = [c for c in 'abcdefghijklmnopqrstuvwxyz']
num_dic = {n: i for i, n in enumerate(char_arr)}
n_class = len(num_dic) # number of class(=number of vocab)

seq_data = ['make', 'need', 'coal', 'word', 'love', 'hate', 'live', 'home', 'hash', 'star']

# TextLSTM Parameters
n_step = 3
n_hidden = 128

def make_batch(seq_data):
    input_batch, target_batch = [], []

    for seq in seq_data:
        input = [num_dic[n] for n in seq[:-1]] # 'm', 'a' , 'k' is input
        target = num_dic[seq[-1]] # 'e' is target
        input_batch.append(np.eye(n_class)[input])
        target_batch.append(target)

    return Variable(torch.Tensor(input_batch)), Variable(torch.LongTensor(target_batch))

class TextLSTM(nn.Module):
    def __init__(self):
        super(TextLSTM, self).__init__()

        self.lstm = nn.LSTM(input_size=n_class, hidden_size=n_hidden)
        self.W = nn.Parameter(torch.randn([n_hidden, n_class]).type(dtype))
        self.b = nn.Parameter(torch.randn([n_class]).type(dtype))

    def forward(self, X):
        input = X.transpose(0, 1)  # X : [n_step, batch_size, n_class]

        hidden_state = Variable(torch.zeros(1, len(X), n_hidden))   # [num_layers(=1) * num_directions(=1), batch_size, n_hidden]
        cell_state = Variable(torch.zeros(1, len(X), n_hidden))     # [num_layers(=1) * num_directions(=1), batch_size, n_hidden]

        # final_hidden_state, final_cell_state : [num_layers(=1) * num_directions(=2), batch_size, n_hidden]
        outputs, (final_hidden_state, final_cell_state) = self.lstm(input, (hidden_state, cell_state))
        outputs = outputs[-1]  # [batch_size, n_hidden]
        model = torch.mm(outputs, self.W) + self.b  # model : [batch_size, n_class]
        return model

input_batch, target_batch = make_batch(seq_data)

model = TextLSTM()

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

output = model(input_batch)

# Training
for epoch in range(1000):
    optimizer.zero_grad()

    output = model(input_batch)
    loss = criterion(output, target_batch)
    if (epoch + 1) % 100 == 0:
        print('Epoch:', '%04d' % (epoch + 1), 'cost =', '{:.6f}'.format(loss))

    loss.backward()
    optimizer.step()

input = [sen[:3] for sen in seq_data]
print(input)

predict = model(input_batch).data.max(1, keepdim=True)[1]

output = []
for pre in [pre for pre in predict]:
    for key, value in num_dic.items():
        if value == pre:
            output.append(key)
print(output)