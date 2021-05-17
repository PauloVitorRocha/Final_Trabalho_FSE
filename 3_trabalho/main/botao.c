#include "./includes/botao.h"

xQueueHandle filaDeInterrupcao;

int clickBotao = 0;

static void IRAM_ATTR gpio_isr_handler(void *args)
{
    int pino = (int)args;
    xQueueSendFromISR(filaDeInterrupcao, &pino, NULL);
}

void inicializaBotao()
{
    filaDeInterrupcao = xQueueCreate(10, sizeof(int));
    // Configuração do pino do Botão
    gpio_pad_select_gpio(BOTAO);
    // Configura o pino do Botão como Entrada
    gpio_set_direction(BOTAO, GPIO_MODE_INPUT);
    // Configura o resistor de Pulldown para o botão (por padrão a entrada estará em Zero)
    gpio_pulldown_en(BOTAO);
    // Desabilita o resistor de Pull-up por segurança.
    gpio_pullup_dis(BOTAO);
    gpio_set_intr_type(BOTAO, GPIO_INTR_POSEDGE);

    gpio_install_isr_service(0);
    gpio_isr_handler_add(BOTAO, gpio_isr_handler, (void *)BOTAO);
}

void trataInterrupcaoBotao(void *params)
{
    int pino;
    int contador = 0;
    while (true)
    {
        printf("entrei aqui\n");
        if (xQueueReceive(filaDeInterrupcao, &pino, portMAX_DELAY))
        {
            // De-bouncing
            int estado = gpio_get_level(pino);
            printf("estado = %d\n", estado);
            if (estado == 1)
            {
                printf("estado =1\n");
                gpio_isr_handler_remove(pino);
                clickBotao = !clickBotao;

                mandaMensagemEstado();
                // Habilitar novamente a interrupção
                vTaskDelay(50 / portTICK_PERIOD_MS);
                gpio_isr_handler_add(pino, gpio_isr_handler, (void *)pino);
            }
        }
    }
}