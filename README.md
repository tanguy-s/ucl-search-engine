# ucl-search-engine

## Testing & Querying the engine

Connect to the server:
```
ssh -i IRDM.pem ec2-user@52.56.165.96
```

Cd to the directory and activate the virtual environment:
```
cd ucl-search-engine
source ../venv/bin/activate
```

Run the following command and follow the instructions
```
./manage.py search
```



## Creating a crawler instance

To create a crawler instance ssh to your server and run:
```
sudo yum install gcc python34 python34-devel mysql mysql-devel libxml2-devel libxslt-devel libjpeg-turbo-devel git && git clone https://github.com/tanguy-s/ucl-search-engine.git && virtualenv venv --distribute -p python3 && source venv/bin/activate && pip install -r ucl-search-engine/requirements.txt && cd ucl-search-engine && sudo cp init_celeryd.sh /etc/init.d/celeryd && sudo chmod +x /etc/init.d/celeryd && sudo cp celeryd /etc/default/ && sudo /etc/init.d/celeryd start
```

## Rebuilding index 
From scratch:
```
./manage.py index --options clear
```

Update:
From scratch:
```
./manage.py index --options update
```
