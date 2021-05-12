#ifndef MAIN_H
#define MAIN_H

#include <stdio.h>
#include <string.h>
#include "nvs_flash.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "freertos/semphr.h"
#include "wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "sdkconfig.h"

// #include "mqtt.h"
#include "dht.h"
#include "led.h"
#include "botao.h"
#include "criaJson.h"

void conectadoWifi(void *params);
void trataComunicacaoComServidor(void *params);

#endif