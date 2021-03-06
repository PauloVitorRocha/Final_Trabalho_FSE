#ifndef CRIA_JSON_H
#define CRIA_JSON_H

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

#include "cJSON.h"
#include "mqtt.h"
#include "dht.h"
#include "led.h"
#include "botao.h"

int criaJson(cJSON *espInfo, cJSON *titulo, char nome[], float info);
void mandaMensagem(char *topico, float info);
void mandaMensagemEstado();
int criaJsonStr(cJSON *espInfo, cJSON *titulo);

#endif