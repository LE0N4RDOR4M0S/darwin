package com.leonardoramos.app.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping
public class Controller {
    @GetMapping("/hello")
    public String hello() {
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return "Hello, World!";
    }
    @GetMapping("/process")
    public String processData(String input) {
        return input.toUpperCase();
    }

    @PostMapping("/compute")
    public int computeSum(int a, int b) {
        return a + b;
    }
}
