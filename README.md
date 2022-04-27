# MuxVId
https://colab.research.google.com/drive/1JePRDbwqvnqaEhHEozHvHlgLvxav9fKP

## Installation
```bash
pip install pymongo[srv]
git clone https://github.com/jackthenewbie/MuxVId.git
```
- https://rclone.org/install/

- https://cloud.mongodb.com/ 
  1. Get connection string here, make a new account,
  2. Security>Database Access> Add new user if you don't have one > create password
  and
  3. Data Deployments>Connect>Connect your application> Choose python 3.6 and up> Copy string
Example:
```
mongodb+srv://john:123456789>@cluster0.npogp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority
```
1. Generate database
```
python3 getTarget.py
```
2. Mux
```
python3 MuxLocal.py
```
##Optional
Removed files already mux (aka exists in destDir in database)
```
python3 checkoutDb.py
```
