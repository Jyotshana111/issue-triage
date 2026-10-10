package com.example.issue_triage_backend;

import java.util.Map;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;

@RestController
public class AnalysisController {

    private final RestClient python = RestClient.create("http://127.0.0.1:8000");

    @PostMapping("/api/analyze")
    public Map<?, ?> analyze(@RequestBody Map<String, String> issue) {
        return python.post()
                .uri("/analyze")
                .body(issue)
                .retrieve()
                .body(Map.class);
    }
}