from db_2026.seccom.common import *

if __name__ == '__main__':
    pub, prv = generate_keypair()
    pus = public_to_string(pub)
    print(pus)
    p_pub = public_from_string(pus)
    print(p_pub == pub)

    write_public_key(pub, 'gg.pub.pem')
    write_private_key(prv, 'gg.prv.pem')
    zpub = load_public_key('gg.pub.pem')
    zprv = load_private_key('gg.prv.pem')
    print('---')
    print(zpub == pub)
    print(zprv == prv)  # False, but bytes are the same; new prv can decode
