cd /usr/share/X11/xorg.conf.d
if [ -f "99-fbdev.conf" ]; then
sudo mv "99-fbdev.conf" "99-fbdev.conf.old"
echo "Touchscreen is now dominant display"
elif [ -f "99-fbdev.conf.old" ]; then
sudo mv "99-fbdev.conf.old" "99-fbdev.conf"
echo "HDMI display is now dominant display"
else
echo "There is no file '99-fbdev.conf'. Create it to switch between the touchscreen and HDMI display."
fi
echo "Will close in 5 seconds."
sleep 5