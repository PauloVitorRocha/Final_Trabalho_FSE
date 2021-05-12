#include <stdio.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include <string.h>
#include "freertos/queue.h"
#include "esp_log.h"
#include "esp_wifi.h"
#include "criaJson.h"
#include "esp_event.h"
#include "nvs_flash.h"
#include "freertos/semphr.h"

#include "led.h"
#include "dht.h"
#include "botao.h"
#include "wifi.h"

#define LED 2
#define GPIO_N4 4

xQueueHandle filaDeInterrupcao;

// xSemaphoreHandle conexaoWifiSemaphore;
xSemaphoreHandle esperaLed;

char *macAddress;

void getMacAddress()
{

    uint8_t *mac = (uint8_t *)malloc(sizeof(uint8_t) * 15);
    esp_efuse_mac_get_default(mac);
    int interm[20];
    macAddress = (char *)malloc(sizeof(char *) * 100);
    for (int i = 0; i < 6; i++)
    {
        interm[i] = mac[i];
        sprintf(macAddress, "%X", interm[i]);
        macAddress += 2;
    }
    macAddress -= 12;
    // printf("MAC ADDRESS = %s\n", macAddress);
}

// static void IRAM_ATTR gpio_isr_handler(void *args)
// {
//     int pino = (int)args;
//     xQueueSendFromISR(filaDeInterrupcao, &pino, NULL);
// }

void getDhtTemperature(void *params)
{
    float temperatura, umidade;
    while (1)
    {
        dht_read_float_data(DHT_TYPE_DHT11, GPIO_N4, &umidade, &temperatura);
        ESP_LOGI("A", "temp: %f, humidity: %f", temperatura, umidade);
        mandaMensagem("temperatura", temperatura);
        mandaMensagem("umidade", umidade);
        mandaMensagemEstado();
        vTaskDelay(2000 / portTICK_PERIOD_MS);
    }
}

// void trataInterrupcaoBotao(void *params)
// {
//     int pino;
//     int contador = 0;
//     int estadoLed = 0;

//     while (true)
//     {
//         if (xQueueReceive(filaDeInterrupcao, &pino, portMAX_DELAY))
//         {
//             // De-bouncing
//             int estado = gpio_get_level(pino);

//             if (estado == 1)
//             {
//                 gpio_isr_handler_remove(pino);
//                 printf("estado= %d, gpio=%d\n", estado, gpio_get_level(pino));
//                 while (gpio_get_level(pino) == estado)
//                 {
//                     printf("Aguardante\n");
//                     vTaskDelay(50 / portTICK_PERIOD_MS);
//                 }

//                 contador++;
//                 printf("AQ\n");
//                 ligaDesligaLed();
//                 printf("Os botões foram acionados %d vezes. Botão: %d\n", contador, pino);

//                 // Habilitar novamente a interrupção
//                 vTaskDelay(50 / portTICK_PERIOD_MS);
//                 gpio_isr_handler_add(pino, gpio_isr_handler, (void *)pino);
//             }
//         }
//     }
// }

void app_main(void)
{
    // Inicializa o NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND)
    {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    inicializaBotao();
    inicializaLed();
    wifi_init();
    getMacAddress();

    esperaLed = xSemaphoreCreateBinary();
    // conexaoWifiSemaphore = xSemaphoreCreateBinary();

    xTaskCreate(trataInterrupcaoBotao, "TrataBotao", 4096, NULL, 1, NULL);
    xTaskCreate(getDhtTemperature, "getTemp", 4096, NULL, 1, NULL);

}
