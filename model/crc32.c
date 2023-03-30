#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

// Programmable CRC pipeline
//   Multiple Polynomials
//   - Polynomial can be injected at runtime and stored and executed
//   - Arbitrary length message
//   - Message done signal
//
// Reference: http://www.sunshine2k.de/articles/coding/crc/understanding_crc.html

typedef uint8_t bool;
#define true (!!1)
#define false (!!0)

struct crc_info {
  const char * name;
  unsigned int bitwidth;
  uint64_t check;
  uint64_t poly;
  uint64_t init;
  bool reflect_in;
  bool reflect_out;
  uint64_t xorout;
};

// CRC parameters ripped from: https://crccalc.com/
struct crc_info configs[] = {
  {"CRC-32", 32,	0xCBF43926,	0x04C11DB7,	0xFFFFFFFF,	true,	true,	0xFFFFFFFF},
  {"CRC-32/BZIP2", 32,	0xFC891918,	0x04C11DB7,	0xFFFFFFFF,	false,	false,	0xFFFFFFFF},
  {"CRC-32/JAMCRC", 32,	0x340BC6D9,	0x04C11DB7,	0xFFFFFFFF,	true,	true,	0x00000000},
  {"CRC-32/MPEG-2", 32,	0x0376E6E7,	0x04C11DB7,	0xFFFFFFFF,	false,	false,	0x00000000},
  {"CRC-32/POSIX", 32,	0x765E7680,	0x04C11DB7,	0x00000000,	false,	false,	0xFFFFFFFF},
  {"CRC-32/SATA", 32,	0xCF72AFE8,	0x04C11DB7,	0x52325032,	false,	false,	0x00000000},
  {"CRC-32/XFER", 32,	0xBD0BE338,	0x000000AF,	0x00000000,	false,	false,	0x00000000},
  {"CRC-32C", 32,	0xE3069283,	0x1EDC6F41,	0xFFFFFFFF,	true,	true,	0xFFFFFFFF},
  {"CRC-32D", 32,	0x87315576,	0xA833982B,	0xFFFFFFFF,	true,	true,	0xFFFFFFFF},
  {"CRC-32Q", 32,	0x3010BF7F,	0x814141AB,	0x00000000,	false,	false,	0x00000000},
  {"CRC-16/ARC", 16,	0xBB3D,	0x8005,	0x0000,	true,	true,	0x0000},
  {"CRC-16/AUG-CCITT", 16,	0xE5CC,	0x1021,	0x1D0F,	false,	false,	0x0000},
  {"CRC-16/BUYPASS", 16,	0xFEE8,	0x8005,	0x0000,	false,	false,	0x0000},
  {"CRC-16/CCITT-FALSE", 16,	0x29B1,	0x1021,	0xFFFF,	false,	false,	0x0000},
  {"CRC-16/CDMA2000", 16,	0x4C06,	0xC867,	0xFFFF,	false,	false,	0x0000},
  {"CRC-16/DDS-110", 16,	0x9ECF,	0x8005,	0x800D,	false,	false,	0x0000},
  {"CRC-16/DECT-R", 16,	0x007E,	0x0589,	0x0000,	false,	false,	0x0001},
  {"CRC-16/DECT-X", 16,	0x007F,	0x0589,	0x0000,	false,	false,	0x0000},
  {"CRC-16/DNP", 16,	0xEA82,	0x3D65,	0x0000,	true,	true,	0xFFFF},
  {"CRC-16/EN-13757", 16,	0xC2B7,	0x3D65,	0x0000,	false,	false,	0xFFFF},
  {"CRC-16/GENIBUS", 16,	0xD64E,	0x1021,	0xFFFF,	false,	false,	0xFFFF},
  {"CRC-16/KERMIT", 16,	0x2189,	0x1021,	0x0000,	true,	true,	0x0000},
  {"CRC-16/MAXIM", 16,	0x44C2,	0x8005,	0x0000,	true,	true,	0xFFFF},
  {"CRC-16/MCRF4XX", 16,	0x6F91,	0x1021,	0xFFFF,	true,	true,	0x0000},
  {"CRC-16/MODBUS", 16,	0x4B37,	0x8005,	0xFFFF,	true,	true,	0x0000},
  {"CRC-16/RIELLO", 16,	0x63D0,	0x1021,	0xB2AA,	true,	true,	0x0000},
  {"CRC-16/T10-DIF", 16,	0xD0DB,	0x8BB7,	0x0000,	false,	false,	0x0000},
  {"CRC-16/TELEDISK", 16,	0x0FB3,	0xA097,	0x0000,	false,	false,	0x0000},
  {"CRC-16/TMS37157", 16,	0x26B1,	0x1021,	0x89EC,	true,	true,	0x0000},
  {"CRC-16/USB", 16,	0xB4C8,	0x8005,	0xFFFF,	true,	true,	0xFFFF},
  {"CRC-16/X-25", 16,	0x906E,	0x1021,	0xFFFF,	true,	true,	0xFFFF},
  {"CRC-16/XMODEM", 16,	0x31C3,	0x1021,	0x0000,	false,	false,	0x0000},
  {"CRC-A", 16,	0xBF05,	0x1021,	0xC6C6,	true,	true,	0x0000},
  {"CRC-8", 8,	0xF4,	0x07,	0x00,	false,	false,	0x00},
  {"CRC-8/CDMA2000", 8,	0xDA,	0x9B,	0xFF,	false,	false,	0x00},
  {"CRC-8/DARC", 8,	0x15,	0x39,	0x00,	true,	true,	0x00},
  {"CRC-8/DVB-S2", 8,	0xBC,	0xD5,	0x00,	false,	false,	0x00},
  {"CRC-8/EBU", 8,	0x97,	0x1D,	0xFF,	true,	true,	0x00},
  {"CRC-8/I-CODE", 8,	0x7E,	0x1D,	0xFD,	false,	false,	0x00},
  {"CRC-8/ITU", 8,	0xA1,	0x07,	0x00,	false,	false,	0x55},
  {"CRC-8/MAXIM", 8,	0xA1,	0x31,	0x00,	true,	true,	0x00},
  {"CRC-8/ROHC", 8,	0xD0,	0x07,	0xFF,	true,	true,	0x00},
  {"CRC-8/WCDMA", 8,	0x25,	0x9B,	0x00,	true,	true,	0x00},
  {"CRC-5/USB", 5,	0x19,	0x05,	0x1f,	true,	true,	0x1f},
  {"CRC-1", 8,	0x1,	0x1,	0x00,	false,	false,	0x00},
};

char *printBin8(uint8_t num)
{
  int i;

  char str[8+1+2];

  str[0] = '0';
  str[1] = 'b';

  for(i = 0; i < 8; i++, num <<= 1)
    str[i+2] = (num & 0x80) ? '1' : '0';

  str[i+2] = '\0';

  return strdup(str);
}

char *printBin32(uint32_t num)
{
  int i;

  char str[32+1+2];

  str[0] = '0';
  str[1] = 'b';

  for(i = 0; i < 32; i++, num <<= 1)
    str[i+2] = (num & 0x80000000) ? '1' : '0';

  str[i+2] = '\0';

  return strdup(str);
}

uint64_t reflect(uint64_t v, unsigned int bitwidth) {
  uint64_t nv = 0;

  for (size_t i = 0; i < bitwidth; i++) {
    if (v & (1 << i))
      nv |= 1 << (bitwidth - i - 1);
  }

  return nv;
}

uint64_t crc_generic(struct crc_info *param, const uint8_t *buf, size_t size) {
  uint64_t bitmask = (1UL << param->bitwidth) - 1;
  uint64_t topbitmask = 1UL << (param->bitwidth-1);

  uint64_t crc = param->init;

  for (size_t i = 0; i < size; i++) {
    uint8_t v = param->reflect_in ? reflect(buf[i], 8) : buf[i];

    crc = crc ^ (v << (param->bitwidth - 8));

    //printf("%08x\n", crc);

    for (size_t b = 0; b < 8; b++) {
      if (crc & topbitmask) {
        crc = ((crc << 1) ^ param->poly) & bitmask;
      } else {
        crc = (crc << 1) & bitmask;
      }
    }
  }

  crc = param->reflect_out ? reflect(crc, param->bitwidth) : crc;

  return crc ^ param->xorout;
}

void crc_datapath1(struct crc_info *param, uint64_t *crc, uint64_t topbitmask, uint64_t bitmask, bool v);

uint64_t crc_generic_unrolled(struct crc_info *param, const uint8_t *buf, size_t size) { 
  uint64_t bitmask = (1UL << param->bitwidth) - 1;
  uint64_t topbitmask = 1UL << (param->bitwidth-1);
  uint64_t crc = param->init;

  for (size_t i = 0; i < size; i++) {
    uint8_t v = buf[i];
    int b = !param->reflect_in ? 7 : 0;
    int dir = !param->reflect_in ? -1 : 1;

    for (int j = 0; j < 8; j++) {
      int bit = !!(v & (1 << b));
      crc_datapath1(param, &crc, topbitmask, bitmask, bit);
      printf("%d.%d: crc=%08x b=%d j=%d\n", i, j, crc, bit & 1, b);
      b += dir;
    }

#if 0
    // Unroll
    crc_datapath1(param, &crc, topbitmask, bitmask, !!(v & (1 << b))); b += dir;
    crc_datapath1(param, &crc, topbitmask, bitmask, !!(v & (1 << b))); b += dir;
    crc_datapath1(param, &crc, topbitmask, bitmask, !!(v & (1 << b))); b += dir;
    crc_datapath1(param, &crc, topbitmask, bitmask, !!(v & (1 << b))); b += dir;

    crc_datapath1(param, &crc, topbitmask, bitmask, !!(v & (1 << b))); b += dir;
    crc_datapath1(param, &crc, topbitmask, bitmask, !!(v & (1 << b))); b += dir;
    crc_datapath1(param, &crc, topbitmask, bitmask, !!(v & (1 << b))); b += dir;
    crc_datapath1(param, &crc, topbitmask, bitmask, !!(v & (1 << b))); b += dir;
#endif
  }

  crc = param->reflect_out ? reflect(crc, param->bitwidth) : crc;
  return crc ^ param->xorout;
}

void crc_datapath1(struct crc_info *param, uint64_t *crc, uint64_t topbitmask, uint64_t bitmask, bool v) {
  bool isset = !!((*crc >> (param->bitwidth - 1)) ^ v);
  uint64_t crc_shifted = (*crc << 1) & bitmask;
  *crc = isset ? (crc_shifted ^ param->poly) : crc_shifted;
}

int main(int argc, char *argv[])
{
  const char *message = "123456789";
  bool default_message = true;

  if(argc > 1)
  {
    message = argv[1];
    default_message = false;
  }

  printf("Message: %s\n", message);

  for (size_t i = 0; i < sizeof(configs)/sizeof(configs[0]); i++) {
    struct crc_info *param = &configs[i];
    uint64_t result = crc_generic_unrolled(param, message, strlen(message));

    const char * check_result = (param->check != result) ? "FAIL" : "PASS";

    if (default_message)
      printf("%s: %08X [%s]\n", param->name, result, check_result);
    else
      printf("%s: %08X\n", param->name, result);
  }

  return 0;
}
