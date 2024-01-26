The `config.py` file exposes the configuration of the Churn classification test.
The scenario configuration holds the following dag where square nodes are data nodes and diamond nodes are tasks
```
                       _________________       __________
                      | initial_dataset |     |   date   |
                      |  (csv)          |     | (pickle) |
                      |_________________|     |__________|
                                      __\______/__
                                     / preprocess \
                                     \____________/
                                      ______|_______
                                     | preprocessed|
                                     |   dataset   |
                                     |_____________|
                                      ______|_____
                                     /    split   \
                                     \____________/
                                         /     |______________
                        ________________/                     \______________
                       |  train dataset |                     | test dataset |
                       |________________|                     |______________|
                      /               \                            |   |
              _______/                 \________________           |   |
             / train \                 / train baseline \          |   |
             \_______/                 \________________/          |   |
                 |                                   |             |   |
             ____|____                  _____________|__          /   /
            |  model |                 | model baseline |        /   /
            |________|                 |________________|       /   /
                 |                                   |         /   /
                 |                                   |        /   /
                 |    _______________________________|_______/   /
                 |   /                               |          /
              ___|__/_                           ____|_________/___
            / predict \                         / predict baseline \
            \_________/                         \__________________/
                 |                                        |
         _______ |_____                           ________|_____________
        |  predictions |                         | predictions baseline |
        |______________|                         |______________________|
          /       |   \___________                   |       \       \
         /        \               |                  |        \       \
        /          \              |                  |         \       \_______
       /            \             |                  |          \              |
   ___|___          _|_____      _|_____           __|____      _\_____      __|____
  /       \        /       \    /       \         /       \    /       \    /       \
 / Compute \      / Compute \  / Compute \       / Compute \  / Compute \  / Compute \
 \    ROC  /      \ Metrics /  \ Results /       \    ROC  /  \ Metrics /  \ Results /
  \_______/        \_______/    \_______/         \_______/    \_______/    \_______/
     /    \            |           |                /    \          |            |
 ___/_    _\___    ____|____    ___|_____       ___/_    _\____   __|______    __|_______
| Roc |  | Auc |  | Metrics |  | Results |     | Roc |  | Auc |  | Metrics |  | Results |
|_____|  |_____|  |_________|  |_________|     |_____|  |_____|  |_________|  |_________|
```
