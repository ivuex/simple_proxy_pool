#! /bin/bash
# https://developers.supportbee.com/blog/setting-up-cucumber-to-run-with-Chrome-on-Linux/
# https://gist.github.com/curtismcmullan/7be1a8c1c841a9d8db2c
# http://stackoverflow.com/questions/10792403/how-do-i-get-chrome-working-with-selenium-using-php-webdriver
# http://stackoverflow.com/questions/26133486/how-to-specify-binary-path-for-remote-chromedriver-in-codeception
# http://stackoverflow.com/questions/40262682/how-to-run-selenium-3-x-with-chrome-driver-through-terminal
# http://askubuntu.com/questions/760085/how-do-you-install-google-chrome-on-ubuntu-16-04

# Versions
CHROME_DRIVER_VERSION=2.44
# SELENIUM_STANDALONE_VERSION=71.0.3578.80
SELENIUM_SUBDIR=

# Remove existing downloads and binaries so we can start from scratch.
sudo apt-get remove -y google-chrome-stable

rm ~/selenium-server-standalone-*.jar
sudo rm /usr/local/bin/selenium-server-standalone.jar

chromedriver_linux64_url=http://chromedriver.storage.googleapis.com/2.44/chromedriver_linux64.zip
chromedriver_linux64=chromedriver_linux64.zip
wget ${chromedriver_linux64_url}
if [ $? == 0 ];then
    echo 下载 ${chromedriver_linux64_url} 为 ${chromedriver_linux64} 完成
fi
if [ -f /usr/local/bin/${chromedriver_linux64} ];then
   echo ${chromedriver_linux64}* 已存在, 尝试一到/tmp/目录 .
   mv /usr/local/bin/${chromedriver_linux64}* /tmp/
   if [ $? != 0];then
       echo 删除失败,使用已经存在的旧的/usr/local/bin/${chromedriver_linux64}, 如果后续流程不能成功，可以手动以管理员权限移动文件
   fi
fi
chromedriver_name=chromedriver
chromdirver_bin_path=/usr/local/bin/${chromedriver_name}
unzip -o -q -d /usr/local/bin ${chromedriver_linux64}
if [[ $? && -f ${chromdirver_bin_path} ]];then
   echo ${chromedriver_linux64} 已解压为${chromdirver_bin_path}.
else
   echo ${chromedriver_linux64} 没有被成功解压到${chromdirver_bin_path}.
fi
sudo chown root:root ${chromdirver_bin_path}
if [[ $? == 0 ]];then
   echo 修改${chromdirver_bin_path}文件所属为root:root成功
fi
sudo chmod 0755 ${chromdirver_bin_path}
if [[ $? == 0 ]];then
   echo 修改${chromdirver_bin_path}文件权限为0755成功
fi

# Install dependencies.
sudo apt-get update -y
sudo apt-get install -y unzip openjdk-8-jre-headless xvfb libxi6 libgconf-2-4

# Install Chrome.
sudo curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
sudo echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
sudo apt-get -y update
sudo apt-get -y install google-chrome-stable
# curl -L -O http://security.ubuntu.com/ubuntu/pool/universe/c/chromium-browser/chromium-browser_71.0.3578.80-0ubuntu0.16.10.1_amd64.deb
# chromium_browser=chromium-browser_71.0.3578.80-0ubuntu0.16.04.1_amd64.deb
# curl -L -o ~/${chromium_browser} http://security.ubuntu.com/ubuntu/pool/universe/c/chromium-browser/${chromium_browser}
# apt install -y ~/${chromium_browser}
# rm ~/${chromium_browser}

# Install ChromeDriver.

# wget -N http://chromedriver.storage.googleapis.com/${SELENIUM_STANDALONE_VERSION}/chromedriver_linux64.zip -P ~/

# Install Selenium.
# wget -N  http://selenium-release.storage.googleapis.com/71.0.3578.80/selenium-server-standalone-2.45.jar -P ~/
wget -N  http://selenium-release.storage.googleapis.com/${CHROME_DRIVER_VERSION}/selenium-server-standalone-${CHROME_DRIVER_VERSION}.0.jar -P ~/
sudo mv -f ~/selenium-server-standalone-${CHROME_DRIVER_VERSION}.0.jar /usr/local/bin/selenium-server-standalone.jar
sudo chown root:root /usr/local/bin/selenium-server-standalone.jar
sudo chmod 0755 /usr/local/bin/selenium-server-standalone.jar

