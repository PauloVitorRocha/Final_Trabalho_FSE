#include "./includes/led.h"

int estadoLed = 1;

void inicializaLed()
{
    gpio_pad_select_gpio(LED);
    gpio_set_direction(LED, GPIO_MODE_OUTPUT);
}

void ligaDesligaLed()
{
    gpio_set_level(LED, estadoLed);
    estadoLed = !estadoLed;
}
void desligaLed()
{
    gpio_set_level(LED, 0);
    estadoLed=0;
}