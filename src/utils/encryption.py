# -*- coding: utf-8 -*-
# @Time    : 2018/11/2 11:38
# @Author  : Will
# @Email   : 864311352@qq.com
# @File    : encryption.py
# @Software: PyCharm

import base64

from Crypto.Cipher import AES  # str不是16的倍数那就补足为16的倍数


class Encryption(object):

    def __init__(self, secret_key: str):
        self.key = secret_key
        self.aes = AES.new(self.add_to_16(self.key), AES.MODE_ECB)  # 初始化加密器

    def encrypt(self, text: str) -> str:
        """
        加密文本
        :param text:需要加密的字符
        :return:加密后的字符
        """
        encrypt_test = self.aes.encrypt(self.add_to_16(text))
        encrypted_text = str(base64.encodebytes(encrypt_test), encoding='utf8').replace('\n', '')  # 加密
        return encrypted_text

    def decrypt(self, encrypted_text: str) -> str:
        """
        文本解密
        :param encrypted_text: 需要解密的字符
        :return: 解密后的字符
        """
        text_decrypted = base64.decodebytes(bytes(encrypted_text, encoding='utf8'))
        text_decrypted = str(self.aes.decrypt(text_decrypted).rstrip(b'\0').decode("utf8"))  # 解密
        return text_decrypted

    @staticmethod
    def add_to_16(text: str) -> bytes:
        while len(text) % 16 != 0:
            text += '\0'
        return str.encode(text)  # 返回bytes
