#include "simpleSerial.hpp"
#include <termios.h>
#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>

SimpleSerial::SimpleSerial(const char * port, uint32_t baud, bool none_blocking)
{ 
  _isConnected = false;
  speed_t baud_rate;
  switch(baud)
  {
    case 0:       baud_rate = B0;     break;
    case 50:      baud_rate = B50;    break;
    case 75:      baud_rate = B75;    break;
    case 110:   baud_rate = B110;   break;
    case 134:   baud_rate = B134;   break;
    case 150:   baud_rate = B150;   break;
    case 200:   baud_rate = B200;   break;
    case 300:   baud_rate = B300;   break;
    case 600:   baud_rate = B600;   break;
    case 1200:    baud_rate = B1200;  break;
    case 1800:    baud_rate = B1800;  break;
    case 2400:    baud_rate = B2400;  break;
    case 4800:    baud_rate = B4800;  break;
    case 9600:    baud_rate = B9600;  break;
    case 19200:   baud_rate = B19200;   break;
    case 38400:   baud_rate = B38400;   break;
    case 57600:   baud_rate = B57600;   break;
    case 115200:  baud_rate = B115200; break;
    case 230400:  baud_rate = B230400; break;
    default:
      printf("Error! wrong boud rate!\n");
      return;
    break;
  }

  _fd = open(port, O_RDWR | O_NOCTTY | O_NDELAY);
  if(_fd == -1)
  {
      printf("Failed to open port %s\n", port);
      return;
  }

  // Set's it to blocking or none blocking!
  if(none_blocking)
    fcntl(_fd, F_SETFL, FNDELAY);
  else
    fcntl(_fd, F_SETFL, 0);

  // Getting the old options of the port to reuse
  struct termios opt;
  tcgetattr(_fd, &opt);

  // Sets the baud rate! B230400
  cfsetispeed(&opt, baud_rate);
  cfsetospeed(&opt, baud_rate);

  // Enable the receiver and set local mode...
  opt.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
  opt.c_oflag &= ~OPOST;

  // sets 8n1 mode
  opt.c_cflag &= ~PARENB;
  opt.c_cflag &= ~CSTOPB;
  opt.c_cflag &= ~CSIZE;
  opt.c_cflag |= CS8;

  // Set the opt
  tcsetattr(_fd, TCSANOW, &opt);
  _isConnected = true;
}

SimpleSerial::~SimpleSerial()
{
  close(_fd);
}

bool SimpleSerial::getC(char *c)
{
  if(read(_fd, c, 1) < 0)
  {
    return false;
  }
  return true;
}

int SimpleSerial::putC(char *buff, int len)
{
  write(_fd, buff, len);
}

int SimpleSerial::putS(char *buff)
{
  putC(buff, strlen(buff));
}
