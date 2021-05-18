#include "./includes/led.h"

int estadoLed = 1;

void inicializaLed()
{
    gpio_pad_select_gpio(LED);
    gpio_set_direction(LED, GPIO_MODE_OUTPUT);
}

void ligaLed()
{
    gpio_set_level(LED, 1);
    estadoLed = 0;
}
void desligaLed()
{
    gpio_set_level(LED, 0);
    estadoLed=1;
}