### 确保安装了selenium包和你的浏览器对应的WebDriver
### pip install selenium
### Edge对应的Webdriver下载网站：https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import numpy as np
import time
import random


### 设计生成回答函数❤
def CollectQuestionaires(n, QuestType, Demand, DriverPath, link):
    """
    现在我们假设有一个问卷星链接link
    还有一个已经下载好的WebDriver,文件路径是DriverPath(可以理解为一个自动打开浏览器对页面进行操作的工具,不同的浏览器有不同的Driver,这里以Edge为例)
    想要生成n份问卷回答
    还有一个按顺序记录了问题要求的向量Demand,Demand的第i个元素包含了对第i个问题的要求,或者提供的信息
    以及一个按顺序记录了问题类型的向量QuestType,问题类型如下：
    0(以一个列表形式表记).填空大题(就是那种有一堆小空的题目),各小题属于1.或2.类问题
    1.可以随便填的填空题,不过需要给定一个填空的范围
    2.有一个想要的答案的填空题
    3.可以随便选的单选题,不过需要给定选项的数量
    4.有一个想要的答案的单选题
    5.可以随便选的多选题,不过需要给定选项的数量
    6.有一个想要的答案的多选题
    """
    # 设置 WebDriver路径
    service = Service(executable_path=DriverPath)
    driver = webdriver.Edge(service=service)

    # 设置显式等待时间，最多等待10秒
    wait = WebDriverWait(driver, 10)

    # 开始回答问题
    for i in range(1, n + 1):
        # 打开问卷页面
        driver.get(link)
        # 等待页面加载，直到提交按钮加载完成
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctlNext"]')))
        # 开始作答第i+1张问卷
        for j in range(len(QuestType)):
            if isinstance(QuestType[j], list):
                for k in range(len(QuestType[j])):
                    if QuestType[j][k] == 1:
                        Ans = driver.find_element(By.XPATH, f'//*[@id="q{j+1}_{k}"]')
                        # 模拟人输入错误内容后删掉重输的行为，降低跳出验证码的概率
                        Ans.send_keys("asdfghj")
                        time.sleep(0.5)
                        for _ in range(len("asdfghj")):
                            Ans.send_keys(Keys.BACK_SPACE)
                            time.sleep(0.1)
                        random_answer = random.choice(Demand[j][k])
                        Ans.send_keys(random_answer)
                    elif QuestType[j][k] == 2:
                        Ans = driver.find_element(By.XPATH, f'//*[@id="q{j+1}_{k}"]')
                        Ans.send_keys(Demand[j][k])
            elif QuestType[j] == 1:
                Ans = driver.find_element(By.XPATH, f'//*[@id="q{j+1}"]')
                # 模拟人输入错误内容后删掉重输的行为，降低跳出验证码的概率
                Ans.send_keys("asdfghj")
                time.sleep(0.5)
                for _ in range(len("asdfghj")):
                    Ans.send_keys(Keys.BACK_SPACE)
                    time.sleep(0.1)
                random_answer = random.choice(Demand[j])
                Ans.send_keys(random_answer)
            elif QuestType[j] == 2:
                Ans = driver.find_element(By.XPATH, f'//*[@id="q{j+1}"]')
                Ans.send_keys(Demand[j])
            elif QuestType[j] == 3:
                option_index = list(range(1, Demand[j] + 1))
                single_choice_options = []
                for k in range(len(option_index)):
                    single_choice_options.append(
                        f'//*[@id="div{j+1}"]/div[2]/div[{option_index[k]}]/div'
                    )
                for _ in range(2):  # 模拟人点错后重点的行为降低验证码的概率
                    random_option_xpath = random.choice(single_choice_options)
                    driver.find_element(By.XPATH, random_option_xpath).click()
            elif QuestType[j] == 4:
                chosen_option_xpath = f'//*[@id="div{j+1}"]/div[2]/div[{Demand[j]}]/div'
                driver.find_element(By.XPATH, chosen_option_xpath).click()
            elif QuestType[j] == 5:
                option_indices = list(range(1, Demand[j] + 1))
                multiple_choice_options = []
                for k in range(len(option_indices)):
                    multiple_choice_options.append(
                        f'//*[@id="div{j+1}"]/div[2]/div[{option_indices[k]}]/div'
                    )
                for l in range(2):  # 模拟人点错后重点的行为降低验证码的概率
                    random_option_xpaths = random.sample(
                        multiple_choice_options,
                        k=random.randint(1, len(option_indices)),
                    )
                    for xpath in random_option_xpaths:
                        checkbox = driver.find_element(By.XPATH, xpath)
                        checkbox.click()
            elif QuestType[j] == 6:
                checkbox_xpaths = []
                for k in range(len(Demand[j])):
                    checkbox_xpaths.append(
                        f'//*[@id="div{j+1}"]/div[2]/div[{Demand[j][k]}]/div'
                    )
                for xpath in checkbox_xpaths:
                    Ans = driver.find_element(By.XPATH, xpath)
                    Ans.click()
            # 每完成一题后最好等待一段时间，太快的话亲测无论如何都过不了验证码，当然即使是这样也不一定就能够过
            each_wait = np.random.normal(2, 0.6)
            time.sleep(each_wait)
        # 提交第i+1张问卷
        submit_button = driver.find_element(By.XPATH, '//*[@id="ctlNext"]')
        submit_button.click()

        # 频繁提交问卷有可能会弹出验证码，在弹出验证码的时候设置暂停并手动处理智能验证（如果能设计一个自动通过验证码的程序的话我已经放弃这个学位了）
        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="rectTop"]'))
            )
            input("请在浏览器中完成验证码验证后，按回车继续...")
        except TimeoutException:
            # 如果没有找到验证码，继续执行后续
            pass

        # 等待页面跳转并加载完成，可根据需要调整等待时间，问卷越长这个时间越久
        time.sleep(1 + np.log(len(QuestType)) / 3)

    # 所有作答完毕，关闭浏览器
    driver.quit()


if __name__ == "__main__":
    ### 以下例
    n = 1  # 想要生成1份回答
    QuestType = [1, 2, 3, 4, 5, 6, [1, 2]]
    Demand = [
        ["zfn", "tjp", "hcn"],
        "chiikawa",
        3,
        1,
        4,
        [1, 2],
        [["姦", "OGC"], "一周一次"],
    ]
    """
    一共七道题,QuestType给出各题的类型,Demand给出各题的要求
    第一题是随便填的填空题,从三个名字中选一个就好
    第二题是有给定答案的填空题,只能填chiikawa
    第三题是有123三个选项的单选题,程序从中随机选一个
    第四题是给定答案的单选题,只能选第1个选项
    第五题是有1234四个选项的多选题,程序从中随便选,选什么和选几个都是随机的
    第六题是有给定答案的多选题,只能选第1和第2个选项
    第七题是一道填空大题,下设两个小题,第一道小题是可以随便填的填空题,可以填姦也可以填OGC;第二道小题是固定答案的填空题,只能填一周一次
    """
    DriverPath = "D:\msedgedriver.exe"  # 设置为你的WebDriver的路径，保证你的WebDriver跟浏览器匹配（版本也需一致），否则就打开不了浏览器
    link = "https://www.wjx.cn/vm/tFIwvWf.aspx#"  # 问卷链接

    CollectQuestionaires(n, QuestType, Demand, DriverPath, link)  # 执行程序❤

### 这个程序的缺点在于需要人工先看一遍每题的性质和题目有多少个选项然后再决定参数。其实这个操作是可以自动化的，但是需要爬虫，我个人不是很懂爬虫而且现在的网站很多都反爬，我不想这辈子都用不了问卷星^^；
### 同时无法直接满足对回答比例的要求，比如说100张问卷要求10%来自老年的其它性别，20%来自青年女性，40%来自老年女性，30%来自中年男性的回答比例，这就需要手动调参然后分批生成。（我有空会想想这个问题怎么解决）
### 此外，也没有考虑一些更加花哨的题型
### 综上所述，这个程序适用于题目数量和每题选项数量都没有那么多，也没有特别复杂的要求的问卷。（就是勉强能满足大部分情况的意思）
