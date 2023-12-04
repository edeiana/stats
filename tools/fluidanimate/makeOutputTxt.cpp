#include <iostream>
#include <fstream>

#include <stdlib.h>
#include <stdint.h>

//#define FILE_SIZE_INT64 8
#define FILE_SIZE_FLOAT 4
#define FILE_SIZE_INT 4

typedef struct _data{

  int64_t id; // <---
  float px, py, pz;
  float hvx, hvy, hvz;
  float vx, vy, vz;

} data;

union __float_and_int {
  uint32_t i;
  float    f;
};

static inline float bswap_float(float x) {
  union __float_and_int __x;

   __x.f = x;
   __x.i = ((__x.i & 0xff000000) >> 24) | ((__x.i & 0x00ff0000) >>  8) |
           ((__x.i & 0x0000ff00) <<  8) | ((__x.i & 0x000000ff) << 24);

  return __x.f;
}

static inline int bswap_int32(int x) {
  return ( (((x) & 0xff000000) >> 24) | (((x) & 0x00ff0000) >>  8) |
           (((x) & 0x0000ff00) <<  8) | (((x) & 0x000000ff) << 24) );
}

static inline int isLittleEndian() {
  union {
    uint16_t word;
    uint8_t byte;
  } endian_test;

  endian_test.word = 0x00FF;
  return (endian_test.byte == 0xFF);
}

void readWriteFile(char const *inFileName, char const *outFileName){

  std::ifstream inFile(inFileName, std::ios::binary);
  if(!inFile){
    std::cerr << "Error opening input file. Aborting." << std::endl;
    abort();
  }

  std::ofstream outFile(outFileName);
  if(!outFile){
    std::cerr << "Error opening output file. Aborting." << std::endl;
    abort();
  }

  float restParticlesPerMeter, restParticlesPerMeter_le;
  int numParticles, numParticles_le;
  inFile.read((char *)&restParticlesPerMeter_le, FILE_SIZE_FLOAT);
  inFile.read((char *)&numParticles_le, FILE_SIZE_INT);
  if(!isLittleEndian()) {
    restParticlesPerMeter = bswap_float(restParticlesPerMeter_le);
    numParticles          = bswap_int32(numParticles_le);
  } else {
    restParticlesPerMeter = restParticlesPerMeter_le;
    numParticles          = numParticles_le;
  }

  outFile << restParticlesPerMeter << std::endl;
  outFile << numParticles << std::endl;

  data buffer;
  float px, py, pz, hvx, hvy, hvz, vx, vy, vz;
  int64_t id;
  for(int i = 0; i < numParticles; ++i){
    inFile.read((char *)&buffer, sizeof(buffer));
    id = buffer.id; // <---
    px = buffer.px;
    py = buffer.py;
    pz = buffer.pz;
    hvx = buffer.hvx;
    hvy = buffer.hvy;
    hvz = buffer.hvz;
    vx = buffer.vx;
    vy = buffer.vy;
    vz = buffer.vz;
//    inFile.read((char *)&id, sizeof(id));
//    inFile.read((char *)&px, FILE_SIZE_FLOAT);
//    inFile.read((char *)&py, FILE_SIZE_FLOAT);
//    inFile.read((char *)&pz, FILE_SIZE_FLOAT);
//    inFile.read((char *)&hvx, FILE_SIZE_FLOAT);
//    inFile.read((char *)&hvy, FILE_SIZE_FLOAT);
//    inFile.read((char *)&hvz, FILE_SIZE_FLOAT);
//    inFile.read((char *)&vx, FILE_SIZE_FLOAT);
//    inFile.read((char *)&vy, FILE_SIZE_FLOAT);
//    inFile.read((char *)&vz, FILE_SIZE_FLOAT);
    if(!isLittleEndian()){
      id  = __builtin_bswap64(id); // __builtin_bswap64() is a specific GCC function // <---
      px  = bswap_float(px);
      py  = bswap_float(py);
      pz  = bswap_float(pz);
      hvx = bswap_float(hvx);
      hvy = bswap_float(hvy);
      hvz = bswap_float(hvz);
      vx  = bswap_float(vx);
      vy  = bswap_float(vy);
      vz  = bswap_float(vz);
    }

    outFile << id << " " << px << " " << py << " " << pz << " " << hvx << " " << hvy << " " << hvz << " " << vx << " " << vy << " " << vz << " " << std::endl; // <---

  }

  inFile.close();
  outFile.close();

}

int main(int argc, char *argv[]){
  readWriteFile(argv[1], argv[2]);

  return 0;
}

