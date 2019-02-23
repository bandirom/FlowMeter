String inputString = "";         // a String to hold incoming data
boolean stringComplete = false;  // whether the string is complete
unsigned long last_millis;
void setup() {
  Serial.begin(57600);
  Serial.println("IN OPERATION MODE");
  inputString.reserve(200);
  randomSeed(analogRead(0));
}

void loop() {

  if (Serial.available()) {
    byte data[20];
    byte _resp = Serial.readBytes(data,20);                // ... считываем и запоминаем
    Serial.println(_resp);
  }

  if (millis() - last_millis > 1500)
  {
    Serial.println("S=" + String(random(100000, 999999)) + " F=" + String(random(100000, 999999)) + " A=aaaaa.aaa T=" + String(random(200, 300)) + ";\r\n");
    last_millis = millis();
  }
}

/*
  void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
  }*/
