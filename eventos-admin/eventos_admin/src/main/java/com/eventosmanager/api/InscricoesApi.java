import com.eventosmanager.models.Inscricao;
import com.google.gson.Gson;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class InscricoesAPi {
    private static final String BASE_URL = AppConfig.get("API_BASE_URL");
    private static final OkHttpClient client = ApiClient.getClient();
    private static final ObjectMapper mapper = new ObjectMapper();
    private static final Gson gson = new Gson();

    public static Inscricao criarInscricaoRapida(Inscricao inscricao) throws IOException {
        
        String jsonBody = gson.toJson(inscricao)
            RequestBody body = RequestBody.create(jsonBody, JSON);

        Request request = new Request.Builder()
                .url(BASE_URL + "/inscricoes/rapida")
                .post(body)
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("Erro ao criar inscrição rápida: " + response.code() + " - " + response.message());
            }
            return Arrays.asList(mapper.readValue(response.body().string(), Evento[].class));
        }
    }
}