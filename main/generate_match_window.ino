

#include <EEPROM.h>

// type used to capture each data point in a sample
// !maximum space in nano is believed to be 1024B!
// in that case, the hard max is 5B per data point
#define USE_TYPE short

// N - number of samples represented in window average
// LO - first sample in window average
// HI - last sample in window average
int BASE = 0;
int LENGTH = 100;

int ADDR_FN  = 0
int ADDR_FLO = ADDR_FN + sizeof(USE_TYPE);
int ADDR_FHI = ADDR_FLO + (LENGTH - 1) * sizeof(USE_TYPE);

int ADDR_EN = ADDR_FHI + sizeof(USE_TYPE);
int ADDR_ELO = ADDR_EN + sizeof(USE_TYPE);
int ADDR_EHI = ADDR_ELO + (LENGTH - 1) * sizeof(USE_TYPE);

int LINEUP = 40;
///////////////////////////////////////////////////////

int addr; 
USE_TYPE val;
USE_TYPE N;

const uint8_t in_pin = A0;
int emg;

int dt_ms = 30;

bool start_fresh = false;
bool align = true;

void setup()
{
  Serial.begin(9600);
  pinMode(in_pin, INPUT);

  if(start_fresh)
  {
    mem_wipe();
  }
}




void mem_wipe()
{
  for (int i = 0; i < EEPROM.length() ; i++)
  {
    EEPROM.update(i, 0)
  }
}

void mem_return()
{
  for(addr = ADDR_FN; addr <= ADDR_FHI; addr += sizeof(USE_TYPE))
  {
    EEPROM.get(addr, val);
    Serial.print(val);
    Serial.print(",");
  }
  Serial.println();

  for(addr = ADDR_EN; addr <= ADDR_EHI; addr += sizeof(USE_TYPE))
  {
    EEPROM.get(addr, val);
    Serial.print(val);
    Serial.print(",");
  }
  Serial.println();
}

void mem_catch_noalign(char command)
{
  // Loop <LENGTH> times with delay <dt_ms> (nom. 100, 30ms)
  // Loop iterates over the address space, stepping by sizeof datapoints.
  // It reads the old value from mem, expands it to maintain an accurate
  // average, and folds a new sensor value into the average window.

  switch (command)
  {
    case 'f':
      EEPROM.get(ADDR_FN, N);

      for (addr = ADDR_FLO; addr <= ADDR_FHI; addr += sizeof(USE_TYPE))
      {
        EEPROM.get(addr, val);
        val *= N;

        emg = analogRead(in_pin);
        val += (short) emg;
        val /= N + 1;

        EEPROM.put(addr, val);
        delay(dt_ms);
      }

      N += 1;
      EEPROM.put(ADDR_FN, N);        
      break;

    case 'e':
      EEPROM.get(ADDR_EN, N);

      for (addr = ADDR_ELO; addr <= ADDR_EHI; addr += sizeof(USE_TYPE))
      {
        EEPROM.get(addr, val);
        val *= N;

        emg = analogRead(in_pin);
        val += (short) emg;
        val /= N + 1;

        EEPROM.put(addr, val);
        delay(dt_ms);
      }

      N += 1;
      EEPROM.put(ADDR_EN, N);        
      break;

    case default:
      return;
      break;
  }
}

void mem_catch(char command)
{
  int emg_arr[LENGTH];
  int max_emg = -1000;
  int max_ind = -1;
  int i;

  int offset;

  for (i = 0; i < LENGTH; i++)
  {
    emg_arr[i] = analogRead(in_pin);

    if (emg_arr[i] > max_emg)
    {
      max_emg = emg_arr[i];
      max_ind = i;
    }

    delay(dt_ms);
  }

  // How far we need to shift
  // - Positive val means pulse is lagging behind, and must be left shifted
  // - Negative val means pulse is too far ahead, and must be right shifted
  offset = max_ind - LINEUP;

  switch (command)
  {
    case 'f':
      i = 0;
      for (addr = ADDR_FLO; addr <= ADDR_FHI; addr += sizeof(USE_TYPE))
      {
        // If the wave is shifted right, extrapolate beginning values
        if (i < offset)
        {
          emg = emg_arr[0];
        }
        // Else if the wave is shifted left, extrapolate end values
        else if (i > (LENGTH - 1 + offset))
        {
          emg = emg_arr[LENGTH - 1];
        }
        // Iterate through the inner values, with actual pulse data
        else
        {
          emg = emg_arr[i + offset];
        }
        i++;

        // Retrieve N and pulse window, fold in the new values
        EEPROM.get(ADDR_FN, N);
        EEPROM.get(addr, val);
        val *= N;

        val += (short) emg;
        val /= N + 1;
        N += 1;

        EEPROM.put(addr, val);
        EEPROM.put(ADDR_FN, N); 
      }

      break;

    case 'e':
      i = 0;
      for (addr = ADDR_ELO; addr <= ADDR_EHI; addr += sizeof(USE_TYPE))
      {
        // If the wave is shifted right, extrapolate beginning values
        if (i < offset)
        {
          emg = emg_arr[0];
        }
        // Else if the wave is shifted left, extrapolate end values
        else if (i > (LENGTH - 1 + offset))
        {
          emg = emg_arr[LENGTH - 1];
        }
        // Iterate through the inner values, with actual pulse data
        else
        {
          emg = emg_arr[i + offset];
        }
        i++;

        // Retrieve N and pulse window, fold in the new values
        EEPROM.get(ADDR_EN, N);
        EEPROM.get(addr, val);
        val *= N;

        val += (short) emg;
        val /= N + 1;
        N += 1;

        EEPROM.put(addr, val);
        EEPROM.put(ADDR_EN, N); 
      }

      break;

    case default:
      return;
      break;
  }
}

void loop()
{
  if( Serial.available() > 0 )
  {
    char in_char = Serial.read();
    switch (in_char)
    {
      // User operated ROM wipe
      case '0':
        mem_wipe();
        break;

      // Returns N followed by window; of flex, then extend (in csv format)
      case 'm':
        mem_return();
        break;

      // Catch new window and fold into memory
      default:
        if (align)
        {
          mem_catch(in_char);
        }
        else
        {
          mem_catch_noalign(in_char);
        }
        break;
    }
  }
}






















