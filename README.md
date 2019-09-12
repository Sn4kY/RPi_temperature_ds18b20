# Photobooth
## Prerequisites
```
sudo apt install python-influxdb python-yaml
echo "# Enable 1-wire
dtoverlay=w1-gpio,gpiopin=5" | sudo tee -a /boot/config.txt
