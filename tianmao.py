from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json
import re

class phone():
    def __init__(self,key,qilaname,qilapassword,page):
        # 设置为chrome浏览器，并确定url,key为要搜索的内容
        option = webdriver.ChromeOptions()
        # 加载启拉的插件
        option.add_argument("load-extension=qila_helper_brower_plugin")
        option.add_experimental_option("excludeSwitches", ["enable-automation"])
        option.add_experimental_option('useAutomationExtension', False)
        # 设置加载模式，当出现我们指定元素页面停止加载
        capa = DesiredCapabilities.CHROME
        capa['pageLoadStrategy'] = "none"

        self.url = 'https://www.tmall.com/'
        self.brower = webdriver.Chrome(chrome_options=option,desired_capabilities=capa)
        # 设置最长等待时间
        self.wait = WebDriverWait(self.brower,30)
        # 搜索的关键字
        self.key = key
        # 启拉插件的账号密码
        self.qilaname = qilaname
        self.qilapassword = qilapassword
        # 用来存放爬取到的所有url
        self.urls = []
        # 设置爬取的页数
        self.page = page
    # 登录启拉助手
    def qilalogin(self,):
        self.brower.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                    })
                  """
        })
        self.brower.get('https://www.qilacps.com/login')
        # 输入账号
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="el-form-item is-error is-required"]//input'))).send_keys(self.qilaname)
        # 输入密码
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="el-form-item is-required"]//input'))).send_keys(self.qilapassword)
        # 点击登录按钮
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="login-container"]//button'))).click()
        time.sleep(1)

    # 登录天猫
    def login(self):
        self.brower.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })
        self.brower.get('https://login.tmall.com/')
        print('请在30秒内扫码登录')
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="sn-container"]/p/span')))
            print('登录成功')
            return True
        except:
            print('登录失败')
            return False

    # 根据输入内容查找并返回所有商品详情页的URL
    def seek(self):
        # 加入cookies
        # if os.path.exists('cookies.txt'):
        #     with open('cookies.txt','r') as f:
        #         cookie = f.read()
        #     f.close()
        #     cookies = json.loads(cookie)
        # else:
        #     print('没有cookie，请生成cookie后再运行')
        #     return False
        # self.brower.get(self.url)
        # for cookie in cookies:
        #     self.brower.add_cookie(cookie)
        # 登录启拉账号
        self.qilalogin()
        if self.login():
            self.brower.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                          get: () => undefined
                        })
                      """
            })
            self.brower.get(self.url)
            # 打开天猫主页，输入key点击搜索按钮
            self.wait.until(EC.presence_of_element_located((By.NAME,'q'))).send_keys(self.key)
            self.wait.until(EC.presence_of_element_located((By.XPATH,'//div[@class="mallSearch-input clearfix"]/button'))).click()
            # 停顿两秒
            time.sleep(2)
            # 点击店铺按钮
            self.wait.until(EC.presence_of_element_located((By.XPATH,"//div[@class='filter clearfix']/a[@class='fType-w ']"))).click()
            # 获取总页数
            page = self.wait.until(EC.presence_of_element_located((By.XPATH,"//div[@class='ui-page-wrap']/b[@class='ui-page-skip']/form"))).text
            pages = re.findall(r"共(.*?)页",page)
            pages = int(pages[0])
            print('搜索到结果共%s页'%pages)
            if self.page > pages:
                self.page = pages
            for i in range(1,int(self.page)+1):
                print('抓取第%s页'%i)
                # 获取第一页时不用点击下一页
                if i > 1:
                    time.sleep(2)
                    self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-page-next'))).click()
                # 这个是商品页获取url
                # links = self.brower.find_elements_by_xpath('//div[@class="view grid-nosku "]//p[@class="productTitle"]/a')
                # 下面这个是通过搜索店铺获取商品url
                links = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,'//div[@class="shopBox  shopBox-expand  j_ShopBox"]/div[2]/div/div[1]/p[2]/a')))
                for link in links:
                    url = link.get_attribute('href')
                    print(url)
                    self.urls.append(url)

                # self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'ui-page-next'))).click()
                time.sleep(2)

        else:
            print('登录失败')
            return False



    # 获取商品详情页URL
    def getphone(self,url):
        self.brower.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                    })
                  """
        })
        self.brower.get(url)

        # 点击电话按钮
        # shopname = self.brower.find_element_by_xpath('//div[@id="shopExtra"]/div/a/strong').text
        shopname = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="shopExtra"]/div/a/strong'))).text

        b = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="qila_helper_container"]/div[@id="qila_helper_nav"]/div[@class="ivu-col ivu-col-span-1"]//button')))
        if b:
            self.brower.execute_script('window.stop();')
            time.sleep(1)
            b.click()
        else:
            self.wait.until(EC.presence_of_element_located((By.XPATH,'//div[@id="qila_helper_container"]/div[@id="qila_helper_nav"]/div[@class="ivu-col ivu-col-span-1"]//button'))).click()


        print('点击成功')
        time.sleep(1)

        # 获取姓名
        username = self.wait.until(EC.presence_of_element_located((By.XPATH,'//div[@class="view-phone-data-container v-transfer-dom"]/div[@class="ivu-modal-wrap"]/div/div/div[@class="ivu-modal-body"]/div/div/p[1]/span[2]'))).text
        # 获取邮箱
        email = self.wait.until(EC.presence_of_element_located((By.XPATH,'//div[@class="view-phone-data-container v-transfer-dom"]/div[@class="ivu-modal-wrap"]/div/div/div[@class="ivu-modal-body"]/div/div/p[2]/span[2]'))).text
        # 获取电话
        phone = self.wait.until(EC.presence_of_element_located((By.XPATH,'//div[@class="view-phone-data-container v-transfer-dom"]/div[@class="ivu-modal-wrap"]/div/div/div[@class="ivu-modal-body"]/div/div/p[3]/span[2]'))).text

        print('店铺名：%s'%shopname)
        print('姓名：%s\n邮箱：%s\n电话：%s\n'%(username,email,phone))
        return shopname,username,email,phone

    #总的调度函数
    def run(self):
        self.seek()
        try:
            with open('shop.txt', 'a') as f:
                for i in self.urls:
                    time.sleep(2)
                    shopname,username,email,phone = self.getphone(i)
                    f.write('店铺名：%s 姓名：%s 邮箱：%s 电话：%s\n' %(shopname,username, email, phone))
            f.close()
            self.brower.close()
        except:
            f.close()
            self.brower.close()
# 由于天猫的cookie加入后依旧无效，此方法放弃
class Cookies():
    def __init__(self):
        # 设置为chrome浏览器，并确定url,key为要搜索的内容
        self.url = 'https://login.tmall.com/'
        self.brower = webdriver.Chrome()
        # 设置最长等待时间
        self.wait = WebDriverWait(self.brower, 30)

    # 扫码登录账号获取cookies
    def login(self):
        self.brower.get(self.url)
        print('请在30秒内扫码登录')
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="sn-container"]/p/span')))
            print('登录成功')
            return True
        except:
            print('登录失败')
            return False

    # 获取cookie保存到本地
    def getcookie(self):
        if self.login():
            cookie = self.brower.get_cookies()
            with open('cookies.txt','w',encoding='utf-8') as f:
                f.write(json.dumps(cookie))
            f.close()
        self.brower.close()

# 爬取前四页
a = phone('古玩','启拉账号','启拉密码',4)
a.run()
