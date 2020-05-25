import time
from Crypto.Cipher import PKCS1_OAEP
import binascii

def HexStringToPNG(filename, newFile):
    data = bytes.fromhex(newFile)
    with open(filename, 'wb') as file:
        file.write(data)
    file.close()


def encryptPNG(filename1, filename2, publicKey, blockSize):

    handler = open(filename1, 'rb')
    hexFile = handler.read().hex()
    posInText = hexFile.find("49444154")

    if posInText != -1:
        length = hexFile[(posInText - 8):posInText]
        chunkLengthDec = int(length, 16)
        realLength = 2 * chunkLengthDec
        idatHex = hexFile[(posInText+8):(posInText + 8 + realLength)]
        newIDAT = ''
        i = 0
        print('orginal lenght')
        print(realLength)

        while i < realLength:
            if (i+blockSize) > realLength:
                block = idatHex[i:i+(realLength-i)]
            else:
                block = idatHex[i:i+blockSize]
            i = i + blockSize
            #print(i)

            encryptedBlock = encryptBlock(block, publicKey, blockSize)


            newIDAT += encryptedBlock
        newIdatLength = int(len(newIDAT) / 2)
        print('encrypted lenght')
        print(2*newIdatLength)
        newIdatLengthHex = format(newIdatLength, 'x')
        while len(newIdatLengthHex) % 8 != 0:
            newIdatLengthHex = '0' + newIdatLengthHex
        newFile = hexFile[0:(posInText-8)] + newIdatLengthHex + hexFile[posInText:(
            posInText+8)] + newIDAT + hexFile[(posInText+realLength):]
        HexStringToPNG(filename2, newFile)


def encryptBlock(block, publicKey, blockSize):
    msg = bytes(block, 'ascii')
    encryptor = PKCS1_OAEP.new(publicKey)

    #blockInt = int(block, 16)
    #dlugosc = len(str(blockInt))
    #if dlugosc > 617:
    #    print('Przekroczono:', dlugosc)

    start = time.time()
    encryptedBlock = encryptor.encrypt(msg)
    end = time.time()
    #print('encrypt time:', str(end - start))
    hexBlock = binascii.hexlify(encryptedBlock)
    hexBlock = str(hexBlock, 'utf-8')
    length = len(hexBlock)
    while len(hexBlock) % 512 != 0:
        hexBlock = '0' + hexBlock
    return hexBlock


def decryptPNG(filename1, filename2, keyPair, blockSize):
    handler = open(filename1, 'rb')
    hexFile = handler.read().hex()
    posInText = hexFile.find("49444154")

    if posInText != -1:
        length = hexFile[(posInText - 8):posInText]
        chunkLengthDec = int(length, 16)
        realLength = 2 * chunkLengthDec
        idatHex = hexFile[(posInText + 8):(posInText + 8 + realLength)]
        newIDAT = ''
        i = 0
        print('new idat length')
        print(realLength)

        while i < realLength:
            block = idatHex[i:i + 512]
            i = i + 512
            decryptedBlock = decryptBlock(block,keyPair,blockSize)
            newIDAT += decryptedBlock
        newIdatLength = int(len(newIDAT) / 2)
        print('decrypted length')
        print(2*newIdatLength)
        newIdatLengthHex = format(newIdatLength, 'x')
        while len(newIdatLengthHex) % 8 != 0:
            newIdatLengthHex = '0' + newIdatLengthHex
        newFile = hexFile[0:(posInText - 8)] + newIdatLengthHex + hexFile[posInText:(
            posInText + 8)] + newIDAT + hexFile[(posInText + realLength):]
        HexStringToPNG(filename2, newFile)


def decryptBlock(block, keyPair, blockSize):
    decryptor = PKCS1_OAEP.new(keyPair)

    blockBytes = str.encode(block)
    hexBlock = decryptor.decrypt(blockBytes)
    hexBlock = binascii.hexlify(hexBlock)
    hexBlock = str(hexBlock, 'utf-8')
    length = len(hexBlock)
    #while len(hexBlock) % blockSize != 0:
   #     hexBlock = '0' + hexBlock
    return hexBlock