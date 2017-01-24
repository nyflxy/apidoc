_author="niyoufa"

# 短链接算法
# 1)将长网址md5生成32位签名串,分为4段, 每段8个字节;
# 2)对这四段循环处理, 取8个字节, 将他看成16进制串与0x3fffffff(30位1)与操作, 即超过30位的忽略处理;
# 3)这30位分成6段, 每5位的数字作为字母表的索引取得特定字符, 依次进行获得6位字符串;
# 4)总的md5串可以获得4个6位串; 取里面的任意一个就可作为这个长url的短url地址;
#

import hashlib

def get_md5(mingwen):
    m = hashlib.md5()
    mdr_str = mingwen.encode()
    m.update(mdr_str)
    ciphertext = m.hexdigest()
    return ciphertext

code_map = (
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
    'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
    'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
    'y', 'z', '0', '1', '2', '3', '4', '5',
    '6', '7', '8', '9', 'A', 'B', 'C', 'D',
    'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
    'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z'
)


def get_hash_key(long_url):
    hkeys = []
    hex = get_md5(long_url)
    for i in range(0, 4):
        n = int(hex[i * 8:(i + 1) * 8], 16)
        v = []
        e = 0
        for j in range(0, 5):
            x = 0x0000003D & n
            e |= ((0x00000002 & n) >> 1) << j
            v.insert(0, code_map[x])
            n = n >> 6
        e |= n << 5
        v.insert(0, code_map[e & 0x0000003D])
        hkeys.append(''.join(v))
    return hkeys[0]


if __name__ == '__main__':
    print(get_hash_key(u'http://180.96.11.69:8500/api/image/list'))