from Crypto.Cipher import AES
import base64


class EnAES(object):
    def __init__(self):
        # self.BS的值为16
        self.BS = AES.block_size
        # 由用户输入的16位或24位或32位长的初始密码字符串 这里的话就是该网站写死的 要从script脚本中细心查找
        self.key = 'qnbyzzwmdgghmcnm'
        # 通过AES处理初始密码字符串，并返回cipher对象
        self.cipher = AES.new(self.key, AES.MODE_ECB)   # 初始化AES实例， 使用ECB模式，源码加密模式就是这样子，key也是一样的

    def pad(self, s):
        """
        PKCS 7 填充方法
        放回的是16倍数长度字符串，填充值是待填充个数，字符串长度必须是16或者是16的倍数 如:
        01 01 01 01 01 01 01 01 长度为8
        填充之后为
        01 01 01 01 01 01 01 01 08 08 08 08 08 08 08 08

        如果传入长度为16 需再填充16个， 如：
        01 01 01 01 01 01 01 01 08 08 08 08 08 08 08 08
        填充之后为
        01 01 01 01 01 01 01 01 08 08 08 08 08 08 08 08 FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
        :param s: 待填充值
        :return: 16倍数长度字符串
        """
        # 填充为16进制 以空白来填充
        return s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)

    def aes_encrypt(self, text):
        """
        text为待破解的数字
        下面的代码是多个语句放在一起
        拆开来就是
        pad_text = self.pad(text)   # 填充
        b_text = bytearray(pad_text, encoding='utf-8')    # 转为byte
        encrypt_text = self.cipher.encrypt(b_text)      # 加密
        encrypt_text_utf-8 = base64.standard_b64encode(encrypt_text).decode('utf-8')[:-2]
            # 将二进制转为utf-8，同时去掉加密字符最后两位俩个等号
        encrypt_text_utf-8_url = encrypt_text_utf-8.replace('/', '^').replace('\\', '^')
            # 替换字符，源码如此
        """
        # return base64.standard_b64encode(self.cipher.encrypt(bytearray(self.pad(text), encoding='utf-8'))
        #                                  ).decode('utf-8')[:-2].replace('/', '^').replace('\\', '^')
        # return base64.standard_b64encode(self.cipher.encrypt(self.pad(text))
        #                          ).decode('utf-8')[:-2].replace('/', '^').replace('\\', '^')
        # 因为需要加密的字符串长度必须为16的倍数、所以使用pad函数进行填充
        pad_text = self.pad(text)
        # print('pad_text : ', pad_text)
        # 输入需要加密的字符串，注意字符串长度要是16的倍数。16,32,48..返回的结果是一个二进制字符串
        encrypt_text = self.cipher.encrypt(pad_text)
        # print('encrypt_text : ', encrypt_text)
        # 将加密后的字符串通过base64编码。（一下是两种base64编码）
        # 至于为什么要把已经加密后的字符串再用base64编码，我觉得是对字符串的处理是基于二进制的，而base64的原理是在每6个二进制数的前面加两个零，这样的话，ascii对处理好的字符串编码就全部可见了
        encrypt_text_utf8 = base64.standard_b64encode(encrypt_text).decode('utf-8')
        # encrypt_text_utf8 = base64.b64encode(encrypt_text).decode('utf-8')
        # print('encrypt_text_utf-8 : ', encrypt_text_utf8.encode())｀
        # print('encrypt_text_utf-8 : ', encrypt_text_utf8)
        return encrypt_text_utf8[:-2]

    def url_encrypt(self, url):
        # 通过分割提取获取到url中的数字id
        url_id = url.split('/')[-1].split('.')[0]
        # print('url_id : ', url_id)
        encrypt_id = self.aes_encrypt(url_id)  # 获取url中的数字"20825",并调用aes_encrypt解密
        url = url.split('/')
        # 获取得到加密后的id进行替换、得到加密后的url
        url[-1] = encrypt_id+'.'+url[-1].split('.')[1]
        return "/".join(url)


def main():
    # url_1 = 'http://ggzy.gzlps.gov.cn/jyxxzczb/20825.jhtml'
    # url_2 = 'http://ggzy.gzlps.gov.cn:80/jyxxzczb/20827.jhtml'
    aes = EnAES()
    """
    在调用之前先初始化这个实例
    后面每一次获取加密链接至需要调用aes.url_encrypt(url)即可
    """

    # print(aes.url_encrypt(url_1))
    # print(aes.url_encrypt(url_2))

aes = EnAES()

# if __name__ == '__main__':
#     main()
