/*
 * This script was made by Koppany Horvath on March 22, 2016
 * It was last updated on April 1, 2016
 * This is under the MIT license and is free to use/modify/distribute
 * as long as proper credits are given
 * 
 * This script is part of the C64Net Project
 * The aim being to give a C64 microcomputer internet access through the
 * cassette port by bitbanging the protocol with an arduino and using a
 * Linux laptop as the internet client.
 * 
 * Setup:
 * Tie sense (f-6) pin to ground and run SAVE command on start
 * Use 22k/47k voltage divider to bring motor control pin from ~7 to ~4.6 volts
 */
const int mpin = 2; //connected to c-3, motor control pin from c64 to arduino
const int wpin = 4; //connected to d-4, output data into c64 from arduino
const int rpin = 3; //connected to e-5, input data from c64 to arduino

uint8_t title[320]; //16 byte title with padding; 320 lms
uint8_t saddr[40]; //2 byte start address; 40 lms
uint8_t eaddr[40]; //2 byte stop address; 40 lms
char filed[1024]; //file data; 1024 bytes max
uint8_t tbyte[20]; //holds single lms byte for processing
unsigned int starta=0, enda=0; //numeric start and end
char ttle[16]; //char title
unsigned int i,j,k; //counter vars
unsigned int s=0, m, l, sze, sml; //small size, med size, long size, temp size (pulseSize), lms func (lms)

void setup(){
  Serial.begin(230400);
  pinMode(mpin,INPUT);
  pinMode(wpin,OUTPUT);
  pinMode(rpin,INPUT);
  pinMode(13,OUTPUT); //status
}

int pulseSize(){ //returns length of pulse
  sze = 0;
  while(digitalRead(rpin) && sze<1000) sze += 1;
  while(!digitalRead(rpin) && sze<2000) sze += 1;
  return sze + 2; }
int lms(){ //returns pulses as 2 for long, 1 for medium, 0 for small
  sml = pulseSize();
  if(sml >= l) return 2;
  if(sml >= m) return 1;
  return 0; }
int trnslt(uint8_t bite[21]){ //returns value of lms byte
  sml = 0;
  for(j=8; j>0; j--){
    sml += bite[j*2];
    sml <<= 1; }
  return sml >> 1; }

/*void singPulse(int len){ //use for single pulses
  digitalWrite(13,LOW);
  while(!digitalRead(mpin)); //pause playback if not motor
  digitalWrite(wpin,LOW);
  delayMicroseconds(len);
  digitalWrite(13,HIGH);
  digitalWrite(wpin,HIGH);
  delayMicroseconds(len);
}
void toPulse(uint8_t bite){ //outputs byte as pulses
  tbyte[0] = 2;
  tbyte[1] = 1;
  for(j=1; j<8; j++){
    if(bitRead(bite,j-1)){ tbyte[j*2] = 1; tbyte[j*2+1] = 0; }
    else{ tbyte[j*2] = 0; tbyte[j*2+1] = 1; }
  }
  if(1^bitRead(bite,0)^bitRead(bite,1)^bitRead(bite,2)^bitRead(bite,3)^bitRead(bite,4)^bitRead(bite,5)^bitRead(bite,6)^bitRead(bite,7)){
    tbyte[18] = 1; tbyte[19] = 0; }
  else{ tbyte[18] = 0; tbyte[19] = 1; }
  for(j=0; j<20; j++){
    if(tbyte[j] == 1) singPulse(m);
    else if(tbyte[j] == 0) singPulse(s);
    else singPulse(l);
  }
}*/

void loop(){
  for(i=0; i<10; i++){
    digitalWrite(13,HIGH);
    delay(100);
    digitalWrite(13,LOW);
    delay(100);
  }
  //first read from c64
  digitalWrite(13,LOW);
  while(!digitalRead(mpin) and !digitalRead(rpin)); //wait for motor and data to start
  digitalWrite(13,HIGH);
  delay(500); //skip first few pulses
  pulseSize(); //sync to pulses
  for(i=0; i<100; i++) s += pulseSize(); //sample 100 small pulses
  s = s/100; //get average size of small pulse
  m = s*1.1; //med pulse is p>=1.1s and p<1.5s
  l = s*1.5; //long pulse is p>=1.5s

  digitalWrite(13,LOW);
  while(lms() != 2); //wait for header start
  digitalWrite(13,HIGH);
  for(i=0; i<179+20; i++) lms(); //skip sync bytes and file type
  for(i=0; i<40; i++) saddr[i] = lms(); //save start addr bytes
  for(i=0; i<40; i++) eaddr[i] = lms(); //save end addr bytes
  for(i=0; i<320; i++) title[i] = lms(); //save filename bytes
  digitalWrite(13,LOW);
  for(i=0; i<3517; i++) lms(); //skip header body and check byte
  while(lms() != 2); //wait for next header
  for(i=0; i<4059; i++) lms(); //skip second header

  for(i=0; i<20; i++) tbyte[i] = saddr[i]; //make numeric start address
  starta = trnslt(tbyte);
  for(i=0; i<20; i++) tbyte[i] = saddr[i+20];
  starta += 16*trnslt(tbyte);
  for(i=0; i<20; i++) tbyte[i] = eaddr[i]; //make numeric end address
  enda = trnslt(tbyte);
  for(i=0; i<20; i++) tbyte[i] = eaddr[i+20];
  enda += 16*trnslt(tbyte);
  for(i=0; i<16; i++){ //make char title
    for(k=0; k<20; k++) tbyte[k] = title[k+(20*i)];
    ttle[i] = trnslt(tbyte);
  }
  
  for(i=0; i<1000; i++) lms(); //skip interrecord gap
  //serial transmit here, adjust skip length accordingly
  Serial.print(char(starta & 255));
  Serial.print(char(starta / 256));
  Serial.print(char(enda & 255));
  Serial.print(char(enda / 256));
  Serial.print(ttle);

  while(lms() != 2); //wait for file start
  digitalWrite(13,HIGH);
  for(i=0; i<179; i++) lms(); //skip sync bytes
  for(i=0; i<enda-starta; i++){ //get file data
    for(k=0; k<20; k++) tbyte[k] = lms();
    filed[i] = trnslt(tbyte);
  }

  for(i=0; i<enda-starta; i++) Serial.print(filed[i]); //print file content

  while(digitalRead(mpin)); //wait for data to stop
  digitalWrite(13,LOW);
  delay(3000);
  
  //-----------------------------------------------------------------------------//
  //-----------------------------------------------------------------------------// 
  /*//then write to c64
  s = 170; //165; //176; //set us/2 of small, med, large pulses
  m = 250; //s*1.454545; //256;
  l = 330; //s*909090; //336;
  
  digitalWrite(wpin,HIGH);
  //serial get addresses, name, data
  while(!Serial.available()); //wait for serial start
  for(i=0; i<4; i++) saddr[i] = Serial.read(); //get start and end addresses
  starta = saddr[0]+saddr[1]*256; enda = saddr[2]+saddr[3]*256;
  for(i=0; i<16; i++) ttle[i] = Serial.read(); //get title
  for(i=0; i<enda-starta; i++) filed[i] = Serial.read(); //get data

  for(i=0; i<5; i++){
    digitalWrite(13,HIGH);
    delay(100);
    digitalWrite(13,LOW);
    delay(100);
  }

  saddr[5] = 0; //make data check value
  for(i=0; i<enda-starta; i++) saddr[5] ^= filed[i];
  saddr[6] = 1^saddr[0]^saddr[1]^saddr[2]^saddr[3]^ttle[0]^ttle[1]^ttle[2]^ttle[3]^ttle[4]^ttle[5]^ttle[6]^ttle[7]^ttle[8]^ttle[9]^ttle[10]^ttle[11]^ttle[12]^ttle[13]^ttle[14]^ttle[15]^32;

  digitalWrite(13,HIGH);
  for(i=0; i<27000; i++) singPulse(s); //leader block 27136
  for(i=137; i>128; i--) toPulse(i); //header sync bytes
  toPulse(1); //file type
  toPulse(saddr[1]); toPulse(saddr[0]); //start address
  toPulse(saddr[3]); toPulse(saddr[2]); //end address
  for(i=0; i<16; i++) toPulse(ttle[i]); //file name
  for(i=0; i<171; i++) toPulse(32); //header body
  toPulse(saddr[6]); //checkbyte
  singPulse(l); singPulse(s); //end header
  
  for(i=0; i<79; i++) singPulse(s); //interblock gap
  
  for(i=9; i>0; i--) toPulse(i); //header2 sync bytes
  toPulse(1); //file type
  toPulse(saddr[0]); toPulse(saddr[1]); //start address
  toPulse(saddr[2]); toPulse(saddr[3]); //end address
  for(i=0; i<16; i++) toPulse(ttle[i]); //file name
  for(i=0; i<171; i++) toPulse(32); //header body
  toPulse(saddr[6]); //checkbyte
  singPulse(l); singPulse(s); //end header

  for(i=0; i<78+5376; i++) singPulse(s); //trailer & interrecord gap
  
  for(i=137; i>128; i--) toPulse(i); //data sync bytes
  for(i=0; i<enda-starta; i++) toPulse(filed[i]); //write data
  toPulse(saddr[5]); //data check byte
  singPulse(l); singPulse(s); //end data

  for(i=0; i<79; i++) singPulse(s); //interblock gap

  for(i=9; i>0; i--) toPulse(i); //data2 sync bytes
  for(i=0; i<enda-starta; i++) toPulse(filed[i]); //write data
  toPulse(saddr[5]); //data check byte
  singPulse(l); singPulse(s); //end data

  for(i=0; i<78; i++) singPulse(s); //trailer
  for(i=0; i<100; i++){ singPulse(l); singPulse(s); }
  digitalWrite(wpin,HIGH);
  digitalWrite(13,LOW);*/
}
