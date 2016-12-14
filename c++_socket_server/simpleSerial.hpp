#include <stdint.h>

class SimpleSerial
{
public:
  SimpleSerial(const char * port, uint32_t baud, bool none_blocking = false);
  // SimpleSerial(const char * port, uint16_t baud) : SimpleSerial(port, baud, false) {};
  ~SimpleSerial();
  
  bool getC(char *c);
  int putC(char *buff, int len);
  int putS(char *buff);
  bool isConnceted() {return _isConnected;}

private:
  bool _isConnected;
  int _fd;
};
