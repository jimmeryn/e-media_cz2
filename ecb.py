import shared
import rsa_algorithm


class ECB():
    def __init__(self, oryginalFile, encryptedFile, decryptedFile, n, e, d, keySize=None, blockSize=None):
        self.oryginalFile = oryginalFile
        self.encryptedFile = encryptedFile
        self.decryptedFile = decryptedFile
        self.n = n
        self.e = e
        self.d = d
        if not keySize:
            keySize = 1024
        self.keySize = keySize
        if not blockSize:
            blockSize = 256
        self.blockSize = blockSize

    def encryptPNG(self):
        handler = open(self.oryginalFile, 'rb')
        hexFile = handler.read().hex()

        # find header
        posInText = shared.findPngHeader(hexFile)

        if posInText != -1:
            realLength = shared.getDataRealLength(hexFile, posInText)
            # get data part from IDAT
            idatHex = hexFile[(posInText+8):(posInText + 8 + realLength)]
            newIDAT = ''

            i = 0

            while i < realLength:
                # jesli dodanie wielkosci bloku wyszlo by poza zakres
                if (i+self.blockSize) > realLength:
                    block = idatHex[i:i+(realLength-i)]
                else:
                    # jesli nie wychodzi poza zakres
                    block = idatHex[i:i+self.blockSize]

                i += self.blockSize
                encryptedBlock = self.encryptBlock(block)
                newIDAT += encryptedBlock

            # sklejanie nowego pliku
            newFile = shared.MakeNewIDAT(
                hexFile, newIDAT, posInText, realLength)
            shared.HexStringToPNG(self.encryptedFile, newFile)

    def encryptBlock(self, block):
        # rzutowanie na int
        blockInt = int(block, 16)
        encryptedBlock = rsa_algorithm.encrypt(blockInt, self.n, self.e)
        # zamiana na hex string bez '0x' z przodu
        hexBlock = format(encryptedBlock, 'x')

        # wyrownanie blokow do dlugosci 512
        while len(hexBlock) % 512 != 0:
            hexBlock = '0' + hexBlock
        return hexBlock

    def decryptPNG(self):
        handler = open(self.encryptedFile, 'rb')
        hexFile = handler.read().hex()
        # find header
        posInText = shared.findPngHeader(hexFile)

        if posInText != -1:
            realLength = shared.getDataRealLength(hexFile, posInText)
            # get data part from IDAT
            idatHex = hexFile[(posInText + 8):(posInText + 8 + realLength)]
            newIDAT = ''
            i = 0

            # wczytywanie blokow o wielkosci 512
            while i < realLength:
                block = idatHex[i:i + 512]
                i += 512
                decryptedBlock = self.decryptBlock(block)
                newIDAT += decryptedBlock

            # sklejanie nowego pliku
            newFile = shared.MakeNewIDAT(
                hexFile, newIDAT, posInText, realLength)
            shared.HexStringToPNG(self.decryptedFile, newFile)

    def decryptBlock(self, block):
        blockInt = int(block, 16)
        encryptedBlock = rsa_algorithm.decrypt(blockInt, self.n, self.d)
        # zamiana na hex string bez '0x' z przodu
        hexBlock = format(encryptedBlock, 'x')

        # wyrownanie dlugosci do parzystej liczby
        while len(hexBlock) % 2 != 0:
            hexBlock = '0' + hexBlock

        return hexBlock
