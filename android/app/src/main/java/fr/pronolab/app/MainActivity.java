package fr.pronolab.app;

import android.annotation.SuppressLint;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.webkit.JavascriptInterface;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Locale;
import org.json.JSONObject;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.webkit.WebViewAssetLoader;

/**
 * Prono Lab : l'application est une page web embarquée (assets/index.html),
 * servie depuis une origine https locale pour que le stockage et les mises à jour en ligne fonctionnent.
 */
public class MainActivity extends AppCompatActivity {

    private static final String HOST = "appassets.androidplatform.net";
    private WebView web;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web = new WebView(this);
        setContentView(web);

        final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .setDomain(HOST)
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setTextZoom(100);

        // Pont réservé à la page embarquée : ouvrir l'application du bookmaker, copier un texte.
        web.addJavascriptInterface(new Bridge(), "ProNoLab");

        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, @NonNull WebResourceRequest request) {
                return loader.shouldInterceptRequest(request.getUrl());
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, @NonNull WebResourceRequest request) {
                Uri u = request.getUrl();
                if (HOST.equals(u.getHost())) return false;
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, u));
                } catch (Exception ignored) { }
                return true;
            }
        });

        if (savedInstanceState != null) {
            web.restoreState(savedInstanceState);
        } else {
            web.loadUrl("https://" + HOST + "/assets/index.html");
        }
    }

    /** Fonctions appelées depuis la page (window.ProNoLab). */
    private class Bridge {
        /** Ouvre l'application installée dont le nom ou l'identifiant contient {@code keyword} ; sinon ouvre {@code fallbackUrl}. Renvoie "app" ou "web". */
        @JavascriptInterface
        public String openApp(String keyword, String fallbackUrl) {
            String k = keyword == null ? "" : keyword.toLowerCase(Locale.ROOT);
            PackageManager pm = getPackageManager();
            Intent main = new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER);
            List<ResolveInfo> apps = pm.queryIntentActivities(main, 0);
            for (ResolveInfo ri : apps) {
                String pkg = ri.activityInfo.packageName.toLowerCase(Locale.ROOT);
                String label = String.valueOf(ri.loadLabel(pm)).toLowerCase(Locale.ROOT);
                if (!k.isEmpty() && (pkg.contains(k) || label.contains(k))) {
                    Intent launch = pm.getLaunchIntentForPackage(ri.activityInfo.packageName);
                    if (launch != null) {
                        launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                        runOnUiThread(() -> startActivity(launch));
                        return "app";
                    }
                }
            }
            if (fallbackUrl != null && fallbackUrl.startsWith("https://")) {
                runOnUiThread(() -> {
                    try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(fallbackUrl))); } catch (Exception ignored) { }
                });
            }
            return "web";
        }

        /** Requête HTTP en arrière-plan, réservée au service de cotes ; résultat renvoyé à window.__nf(id, statut, corps, restants, utilisés). */
        @JavascriptInterface
        public void fetchAsync(String id, String url) {
            new Thread(() -> {
                int code = 0; String body = "", remaining = "", used = "";
                if (url != null && url.startsWith("https://api.the-odds-api.com/")) {
                    HttpURLConnection c = null;
                    try {
                        c = (HttpURLConnection) new URL(url).openConnection();
                        c.setConnectTimeout(15000); c.setReadTimeout(20000);
                        code = c.getResponseCode();
                        InputStream in = code >= 400 ? c.getErrorStream() : c.getInputStream();
                        if (in != null) {
                            ByteArrayOutputStream bo = new ByteArrayOutputStream(); byte[] buf = new byte[8192]; int n;
                            while ((n = in.read(buf)) > 0) bo.write(buf, 0, n);
                            body = new String(bo.toByteArray(), StandardCharsets.UTF_8);
                        }
                        String r = c.getHeaderField("x-requests-remaining"); if (r != null) remaining = r;
                        String u = c.getHeaderField("x-requests-used"); if (u != null) used = u;
                    } catch (Exception e) {
                        code = 0;
                    } finally { if (c != null) c.disconnect(); }
                }
                final String js = "window.__nf(" + JSONObject.quote(id) + "," + code + "," + JSONObject.quote(body) + ","
                        + JSONObject.quote(remaining) + "," + JSONObject.quote(used) + ")";
                runOnUiThread(() -> web.evaluateJavascript(js, null));
            }).start();
        }

        @JavascriptInterface
        public boolean copy(String text) {
            try {
                ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                cm.setPrimaryClip(ClipData.newPlainText("Prono Lab", text));
                return true;
            } catch (Exception e) {
                return false;
            }
        }
    }

    @Override
    protected void onSaveInstanceState(@NonNull Bundle outState) {
        super.onSaveInstanceState(outState);
        web.saveState(outState);
    }

    @SuppressWarnings("deprecation")
    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }
}
