bool repeat = true;

#define RaspberrySerial Serial
#define ControllerSerial Serial1
#define HeaterSerial Serial2

//Baud rate for autotherm heater
#define baudRate 9600
//delay in ms
#define serial_timeout 20

//Light toggling variables
#define freq 500
bool lightOn = false;
long loopTimer = 0;

void setup() {
  HeaterSerial.begin(baudRate);
  ControllerSerial.begin(baudRate);
  RaspberrySerial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
}
void loop() {
  digitalWrite(LED_BUILTIN, lightOn);
  if (millis() > (loopTimer + freq)) {
    loopTimer = millis();
    lightOn = !lightOn;
  }

  if ((HeaterSerial.available() > 0) || (ControllerSerial.available() > 0) || (RaspberrySerial.available() > 0)) {
    runSerial();
  }
}


void runSerial() {
  //RaspberrySerial.println("Data in.");
  if (repeat) {
    //we are in just repeat mode
    if (HeaterSerial.available() > 0) {
      delay(serial_timeout);
      RaspberrySerial.print("H >> ");
      while (HeaterSerial.available() > 0) {
        char inByte = HeaterSerial.read();
        ControllerSerial.write(inByte);
        RaspberrySerial.print("0X");
        RaspberrySerial.print(inByte, HEX);
        RaspberrySerial.print(" ");
      }
      RaspberrySerial.println("");
    }
    if (ControllerSerial.available() > 0) {
      delay(serial_timeout);
      RaspberrySerial.print("C >> ");
      while (ControllerSerial.available() > 0) {
        char inByte = ControllerSerial.read();
        HeaterSerial.write(inByte);
        RaspberrySerial.print("0X");
        RaspberrySerial.print(inByte, HEX);
        RaspberrySerial.print(" ");
      }
      RaspberrySerial.println("");
    }
  } else {
  }

  if (RaspberrySerial.available() > 0) {
    char inByte = RaspberrySerial.read();
    if (inByte == 'R') {
      repeat = true;
    }
    if (inByte == 'S') {
      repeat = false;
    }

    if(inByte =='F'){
      RaspberrySerial.println("Shuting down.");
      HeaterSerial.write(0xAA);
      HeaterSerial.write(0x03);
      HeaterSerial.write(0x00);
      HeaterSerial.write(0x00);
      HeaterSerial.write(0x03);
      HeaterSerial.write(0x5d);
      HeaterSerial.write(0x7c);
    }

    if(inByte =='r'){
      RaspberrySerial.println("Sending raw.");
      delay(5);
      while(RaspberrySerial.available()>0){
        HeaterSerial.write(RaspberrySerial.read());
      }
    }
  }
}
