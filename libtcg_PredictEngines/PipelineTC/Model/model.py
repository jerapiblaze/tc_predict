import torch

from torchsummary import summary
from torch import nn 
import torch.nn.functional as F

class Block(nn.Module):
    def __init__(self, 
                 inp_channels = 64, 
                 out_channels = 64, 
                 is_down = False):
        super().__init__()
        
        self.conv1 = nn.Conv2d(inp_channels,
                               out_channels,
                               kernel_size = 3,
                               stride = 2 if is_down else 1,
                               padding = 1,
                               bias = False)
        
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(True)
        self.conv2 = nn.Conv2d(out_channels,
                               out_channels,
                               kernel_size = 3,
                               stride = 1,
                               padding = 1,
                               bias = False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        self.is_down = is_down
        self.down = nn.Sequential(
            nn.Conv2d(inp_channels, out_channels, kernel_size=1, stride=2, bias=False),
            nn.BatchNorm2d(out_channels)
        )
        
    def forward(self, x):
        x0 = x.clone()
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.conv2(x)
        x = self.bn2(x)
        
        if self.is_down:
            x0 = self.down(x0)
            
        x = x + x0
        x = self.relu(x)
        
        return x
    
class Resnet(nn.Module):
    def __init__(self, 
                 inp_channels = 131, 
                 f_channels = 64, 
                 num_residual_block = [2, 2, 2, 2], 
                 num_class = 2):
        super().__init__()
        self.f_channels = f_channels
        self.conv1 = nn.Conv2d(inp_channels,
                               out_channels = self.f_channels,
                               kernel_size = 7,
                               stride = 2,
                               padding = 3,
                               bias = False)
        self.bn1 = nn.BatchNorm2d(self.f_channels)
        self.relu = nn.ReLU(True)
        self.maxpool = nn.MaxPool2d(kernel_size=3,
                                    stride = 2,
                                    padding = 1,)
        self.resnet, out_channels = self.resnet_layer(num_residual_block)
        
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(in_features = out_channels,
                            out_features = num_class,
                            bias = True)
        self.sm = nn.Softmax(dim=1)
    
    def resnet_layer(self, num_residual_block):
        resnet = []
        inp_channels = out_channels = self.f_channels
        is_down = False
        
        for numBlock in num_residual_block:
            for _ in range(numBlock):
                resnet.append(Block(inp_channels, out_channels, is_down))
                inp_channels = out_channels
                is_down = False
            is_down = True
            out_channels = inp_channels * 2
        
        return nn.Sequential(*resnet), out_channels // 2
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        x = self.resnet(x)
        x = self.avgpool(x)
        x = torch.flatten(x,1)
        x = self.fc(x)
        # x = self.sm(x)
        return x

class CNN2D(nn.Module):
    def __init__(self):
        super(CNN2D, self).__init__()
        # First convolutional layer
        self.conv1 = nn.Conv2d(in_channels=131, out_channels=32, kernel_size=3, padding=1)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Second convolutional layer
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Third convolutional layer
        self.conv3 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Fully connected layers
        self.fc1 = nn.Linear(128 * 2 * 2, 32)
        self.fc4 = nn.Linear(32, 1)

    def forward(self, x):
        # Apply first convolutional layer with ReLU activation and max pooling
        x = self.pool1(F.relu(self.conv1(x)))
        # Apply second convolutional layer with ReLU activation and max pooling
        x = self.pool2(F.relu(self.conv2(x)))
        # Apply third convolutional layer with ReLU activation and max pooling
        x = self.pool3(F.relu(self.conv3(x)))
        # Flatten the output
        x = x.view(x.size(0), -1)
        # Apply fully connected layers with ReLU activation
        x = F.relu(self.fc1(x))
        # Apply output layer with sigmoid activation
        x = torch.sigmoid(self.fc4(x))
        return x
    
if __name__ == '__main__':
    model = Resnet(num_residual_block=[3,4,6,3])
    print(summary(model, (131, 17, 17)))