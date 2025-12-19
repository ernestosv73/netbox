echo "crear directorio"
mkdir ansible-netbox
sleep 1
echo "cambiar a directorio"
cd ansible-netbox
sleep 1
echo "crear contenedor"
python3 -m venv .
sleep 1
source bin/activate
sleep 1
echo "install pynetbox"
pip3 install pynetbox
sleep 2
echo "install ansible"
pip install ansible
sleep 5
echo "install netaddr"
pip install netaddr
sleep 1
echo "install pytz"
pip install pytz
sleep 1
