apt-get install -y python3
apt-get install -y python3-pip
apt install -y python3.12-venv
python3 -m venv env_graphdb
env_graphdb/bin/pip install -r /extern_data/data/requirements/requirements.txt
chmod +x /tmp/env_graphdb/bin/activate
source /tmp/env_graphdb/bin/activate
echo "Python environment installed !"
