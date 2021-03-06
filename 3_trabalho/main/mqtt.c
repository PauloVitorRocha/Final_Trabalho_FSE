#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "esp_system.h"
#include "esp_event.h"
#include "esp_netif.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"

#include "lwip/sockets.h"
#include "lwip/dns.h"
#include "lwip/netdb.h"

#include "esp_log.h"
#include "mqtt_client.h"

#include "./includes/main.h"
#include "./includes/myNvs.h"
#include "./includes/mqtt.h"
#include "esp_sleep.h"
#include "esp32/rom/uart.h"
#include "driver/rtc_io.h"

#define TAG "MQTT"

extern xSemaphoreHandle conexaoMQTTSemaphore;
esp_mqtt_client_handle_t client;
char *macAddress;
char topicoComodo[300];
int isLowPower=0;
int reset=0;

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
}

void conexaoEsp()
{   
    char topicoMqttConnected[100] = "fse2020/170062465/dispositivos/";
    getMacAddress();
    strcat(topicoMqttConnected, macAddress);

    cJSON *mqtt = cJSON_CreateObject();
    if (mqtt == NULL)
    {
        ESP_LOGE("CONEXAOSV", "erro ao criar o objeto json, tentando novamente em 3 segundos\n");
        return;
    }
    cJSON *message = NULL;
    message = cJSON_CreateString(macAddress);
    cJSON_AddItemToObject(mqtt, "id", message);
    char *info = cJSON_Print(mqtt);

    printf("manda mensagem(conexaoEsp) com ID da esp no topico de dispositivos\n");
    mqtt_envia_mensagem(topicoMqttConnected, info);
    mqtt_inscricao(topicoMqttConnected);
}

void mqtt_inscricao(char *topico)
{
    int message_id = esp_mqtt_client_subscribe(client, topico, 0);
    printf("Se cadastra(subscribe) no topico %s\n", topico);
    ESP_LOGI(TAG, "Inscrição enviada, ID: %d", message_id);
}

void pega_Comodo_MQTT_DATA(char buffer[])
{

    cJSON *jsonComodo = cJSON_Parse(buffer);
    cJSON *jsonRestart = cJSON_Parse(buffer);
    const cJSON *atributte = NULL;
    const cJSON *shouldReset = NULL;
    
    atributte = cJSON_GetObjectItemCaseSensitive(jsonComodo, "comodo");
    if (cJSON_IsString(atributte) && (atributte->valuestring != NULL))
    {
        strcpy(topicoComodo, "fse2020/170062465/");
        strcat(topicoComodo, atributte->valuestring);
        grava_valor_nvs();
        cJSON_Delete(jsonComodo);
        xSemaphoreGive(conexaoMQTTSemaphore);
    }
    else
    {
        atributte = cJSON_GetObjectItemCaseSensitive(jsonComodo, "saida");
        if (cJSON_IsNumber(atributte) && (atributte->valueint == 0))
        {
            desligaLed(atributte->valueint);
        }
        atributte = cJSON_GetObjectItemCaseSensitive(jsonComodo, "saida");
        if (cJSON_IsNumber(atributte) && (atributte->valueint == 1))
        {
            ligaLed(atributte->valueint);
        }
    }
    shouldReset = cJSON_GetObjectItemCaseSensitive(jsonRestart, "reset");
    if (cJSON_IsNumber(shouldReset) && (shouldReset->valueint == 1))
    {
        reset = shouldReset->valueint;
        printf("Hora de resetar\n");
        desligaLed();
        erase_nvs();
        esp_restart();
    }
}

static esp_err_t mqtt_event_handler_cb(esp_mqtt_event_handle_t event)
{
    // int msg_id;

    switch (event->event_id)
    {
    case MQTT_EVENT_CONNECTED:
        ESP_LOGI(TAG, "MQTT_EVENT_CONNECTED");
        conexaoEsp();
        if (le_valor_nvs() == -1)
        {
            sprintf(topicoComodo, "fse2020/170062465");
        }
        else
        {
            xSemaphoreGive(conexaoMQTTSemaphore);
            printf("%s\n", topicoComodo);
        }
        break;
    case MQTT_EVENT_DISCONNECTED:
        ESP_LOGI(TAG, "MQTT_EVENT_DISCONNECTED");
        break;

    case MQTT_EVENT_SUBSCRIBED:
        ESP_LOGI(TAG, "MQTT_EVENT_SUBSCRIBED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_UNSUBSCRIBED:
        ESP_LOGI(TAG, "MQTT_EVENT_UNSUBSCRIBED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_PUBLISHED:
        ESP_LOGI(TAG, "MQTT_EVENT_PUBLISHED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_DATA:
        ESP_LOGI(TAG, "MQTT_EVENT_DATA");
        printf("TOPIC=%.*s\r\n", event->topic_len, event->topic);
        printf("DATA=%.*s\r\n", event->data_len, event->data);
        char buffer[100];
        memcpy(buffer, event->data, event->data_len);
        buffer[event->data_len] = '\0';
        pega_Comodo_MQTT_DATA(buffer);
        break;
    case MQTT_EVENT_ERROR:
        ESP_LOGI(TAG, "MQTT_EVENT_ERROR");
        break;
    default:
        ESP_LOGI(TAG, "Other event id:%d", event->event_id);
        break;
    }
    return ESP_OK;
}

static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    ESP_LOGD(TAG, "Event dispatched from event loop base=%s, event_id=%d", base, event_id);
    mqtt_event_handler_cb(event_data);
}

void mqtt_start()
{
    esp_mqtt_client_config_t mqtt_config = {
        .uri = "mqtt://test.mosquitto.org",
    };
    client = esp_mqtt_client_init(&mqtt_config);
    esp_mqtt_client_register_event(client, ESP_EVENT_ANY_ID, mqtt_event_handler, client);
    esp_mqtt_client_start(client);
}

void mqtt_envia_mensagem(char *topico, char *mensagem)
{
    int message_id = esp_mqtt_client_publish(client, topico, mensagem, 0, 1, 0);
    printf("manda msg(mqtt_envia_mensagem): %s para topico %s\n", mensagem, topico);
    ESP_LOGI(TAG, "Mensagem enviada, ID: %d", message_id);
}