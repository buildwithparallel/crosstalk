package com.buildwithparallel.crosstalk;

import android.Manifest;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.net.HttpURLConnection;
import java.net.URL;

public final class CrosstalkActivity extends Activity {
    private static final String LOCAL_ORIGIN = "http://localhost:8000";
    private static final String STATUS_URL = LOCAL_ORIGIN + "/api/v1/status";
    private static final String TERMUX_PACKAGE = "com.termux";
    private static final String TERMUX_PERMISSION = "com.termux.permission.RUN_COMMAND";
    private static final String TERMUX_RUNNER = "/data/data/com.termux/files/usr/bin/crosstalk-android-server";
    private static final int REQUEST_TERMUX = 1001;
    private static final int REQUEST_AUDIO = 1002;
    private static final int REQUEST_FILE = 1003;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private WebView webView;
    private TextView status;
    private TextView offlineMessage;
    private LinearLayout offlinePanel;
    private ValueCallback<Uri[]> fileCallback;
    private PermissionRequest audioPermissionRequest;
    private int probeGeneration;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(Color.BLACK);
        getWindow().setNavigationBarColor(Color.BLACK);
        WebView.setWebContentsDebuggingEnabled(false);
        setContentView(createContent());
        configureWebView();
        probeBackend(true);
    }

    private View createContent() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.BLACK);

        LinearLayout toolbar = new LinearLayout(this);
        toolbar.setOrientation(LinearLayout.HORIZONTAL);
        toolbar.setGravity(Gravity.CENTER_VERTICAL);
        toolbar.setPadding(dp(16), 0, dp(12), 0);
        toolbar.setBackgroundColor(Color.rgb(5, 7, 12));
        root.addView(toolbar, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(48)));

        TextView title = new TextView(this);
        title.setText("CROSSTALK");
        title.setTextColor(Color.WHITE);
        title.setTextSize(15);
        title.setLetterSpacing(0.12f);
        title.setGravity(Gravity.CENTER_VERTICAL);
        toolbar.addView(title, new LinearLayout.LayoutParams(0,
                ViewGroup.LayoutParams.MATCH_PARENT, 1f));

        status = new TextView(this);
        status.setText("CHECKING");
        status.setTextColor(Color.rgb(110, 168, 255));
        status.setTextSize(11);
        status.setGravity(Gravity.CENTER);
        status.setPadding(dp(10), 0, dp(10), 0);
        status.setBackground(rounded(Color.rgb(10, 20, 38), Color.rgb(35, 76, 132), 14));
        toolbar.addView(status, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, dp(28)));

        FrameLayout content = new FrameLayout(this);
        root.addView(content, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));

        webView = new WebView(this);
        webView.setBackgroundColor(Color.BLACK);
        content.addView(webView, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        offlinePanel = new LinearLayout(this);
        offlinePanel.setOrientation(LinearLayout.VERTICAL);
        offlinePanel.setGravity(Gravity.CENTER);
        offlinePanel.setPadding(dp(28), dp(28), dp(28), dp(28));
        offlinePanel.setBackgroundColor(Color.BLACK);
        content.addView(offlinePanel, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        TextView heading = new TextView(this);
        heading.setText("LOCAL NODE OFFLINE");
        heading.setTextColor(Color.WHITE);
        heading.setTextSize(20);
        heading.setLetterSpacing(0.08f);
        heading.setGravity(Gravity.CENTER);
        offlinePanel.addView(heading, matchWrap(dp(12)));

        offlineMessage = new TextView(this);
        offlineMessage.setText("Waiting for the Crosstalk backend on localhost:8000.");
        offlineMessage.setTextColor(Color.rgb(165, 175, 194));
        offlineMessage.setTextSize(14);
        offlineMessage.setGravity(Gravity.CENTER);
        offlinePanel.addView(offlineMessage, matchWrap(dp(24)));

        Button start = actionButton("START LOCAL BACKEND", true);
        start.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) { requestBackendStart(); }
        });
        offlinePanel.addView(start, matchButton());

        Button retry = actionButton("RETRY", false);
        retry.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) { probeBackend(false); }
        });
        offlinePanel.addView(retry, matchButton());

        Button setup = actionButton("OPEN TERMUX", false);
        setup.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) { openTermux(); }
        });
        offlinePanel.addView(setup, matchButton());

        return root;
    }

    private LinearLayout.LayoutParams matchWrap(int bottomMargin) {
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        params.bottomMargin = bottomMargin;
        return params;
    }

    private LinearLayout.LayoutParams matchButton() {
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(48));
        params.topMargin = dp(8);
        return params;
    }

    private Button actionButton(String text, boolean primary) {
        Button button = new Button(this);
        button.setText(text);
        button.setTextSize(12);
        button.setTextColor(primary ? Color.WHITE : Color.rgb(150, 183, 235));
        button.setAllCaps(false);
        button.setBackground(rounded(primary ? Color.rgb(0, 97, 253) : Color.rgb(7, 13, 24),
                primary ? Color.rgb(0, 97, 253) : Color.rgb(35, 51, 80), 12));
        return button;
    }

    private GradientDrawable rounded(int fill, int stroke, int radiusDp) {
        GradientDrawable value = new GradientDrawable();
        value.setColor(fill);
        value.setCornerRadius(dp(radiusDp));
        value.setStroke(dp(1), stroke);
        return value;
    }

    private void configureWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(false);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        if (android.os.Build.VERSION.SDK_INT >= 26) settings.setSafeBrowsingEnabled(true);

        webView.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return routeUrl(request.getUrl());
            }

            @Override public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return routeUrl(Uri.parse(url));
            }

            @Override public void onPageFinished(WebView view, String url) {
                if (isLocal(url)) setOnline();
            }

            @Override public void onReceivedError(WebView view, WebResourceRequest request,
                                                   WebResourceError error) {
                if (request.isForMainFrame()) showOffline("The local backend stopped responding.");
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback,
                                                        FileChooserParams params) {
                if (fileCallback != null) fileCallback.onReceiveValue(null);
                fileCallback = callback;
                try {
                    Intent chooser = params.createIntent();
                    chooser.addCategory(Intent.CATEGORY_OPENABLE);
                    startActivityForResult(chooser, REQUEST_FILE);
                    return true;
                } catch (ActivityNotFoundException error) {
                    fileCallback = null;
                    toast("No file picker is available");
                    return false;
                }
            }

            @Override public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(new Runnable() {
                    @Override public void run() {
                        if (!isLocal(request.getOrigin().toString()) ||
                                !contains(request.getResources(), PermissionRequest.RESOURCE_AUDIO_CAPTURE)) {
                            request.deny();
                            return;
                        }
                        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                            request.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
                        } else {
                            audioPermissionRequest = request;
                            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQUEST_AUDIO);
                        }
                    }
                });
            }
        });
    }

    private boolean contains(String[] values, String wanted) {
        for (String value : values) if (wanted.equals(value)) return true;
        return false;
    }

    private boolean routeUrl(Uri uri) {
        if (isLocal(uri.toString())) return false;
        String scheme = uri.getScheme();
        if (!"http".equalsIgnoreCase(scheme) && !"https".equalsIgnoreCase(scheme)) return true;
        try { startActivity(new Intent(Intent.ACTION_VIEW, uri)); }
        catch (ActivityNotFoundException error) { toast("No browser is available"); }
        return true;
    }

    private boolean isLocal(String url) {
        return url != null && (url.equals(LOCAL_ORIGIN) || url.startsWith(LOCAL_ORIGIN + "/") ||
                url.equals("http://127.0.0.1:8000") || url.startsWith("http://127.0.0.1:8000/"));
    }

    private void probeBackend(final boolean startWhenOffline) {
        final int generation = ++probeGeneration;
        status.setText("CHECKING");
        new Thread(new Runnable() {
            @Override public void run() {
                final boolean online = backendResponds();
                handler.post(new Runnable() {
                    @Override public void run() {
                        if (generation != probeGeneration || isFinishing()) return;
                        if (online) {
                            setOnline();
                            if (!isLocal(webView.getUrl())) webView.loadUrl(LOCAL_ORIGIN);
                        } else if (startWhenOffline && hasTermuxPermission() && isTermuxInstalled()) {
                            startBackend();
                        } else {
                            showOffline("Waiting for the Crosstalk backend on localhost:8000.");
                        }
                    }
                });
            }
        }, "crosstalk-probe").start();
    }

    private boolean backendResponds() {
        HttpURLConnection connection = null;
        try {
            connection = (HttpURLConnection)new URL(STATUS_URL).openConnection();
            connection.setConnectTimeout(1200);
            connection.setReadTimeout(1200);
            connection.setUseCaches(false);
            return connection.getResponseCode() == 200;
        } catch (Exception ignored) {
            return false;
        } finally {
            if (connection != null) connection.disconnect();
        }
    }

    private void requestBackendStart() {
        if (!isTermuxInstalled()) {
            showOffline("Termux is required to run the local Python backend.");
            return;
        }
        if (!hasTermuxPermission()) {
            requestPermissions(new String[]{TERMUX_PERMISSION}, REQUEST_TERMUX);
            return;
        }
        startBackend();
    }

    private void startBackend() {
        status.setText("STARTING");
        offlineMessage.setText("Starting the private localhost backend through Termux…");
        try {
            Intent command = new Intent("com.termux.RUN_COMMAND");
            command.setClassName(TERMUX_PACKAGE, "com.termux.app.RunCommandService");
            command.putExtra("com.termux.RUN_COMMAND_PATH", TERMUX_RUNNER);
            command.putExtra("com.termux.RUN_COMMAND_ARGUMENTS", new String[]{"start"});
            command.putExtra("com.termux.RUN_COMMAND_WORKDIR", "/data/data/com.termux/files/home");
            command.putExtra("com.termux.RUN_COMMAND_BACKGROUND", true);
            startService(command);
            pollUntilReady(0);
        } catch (RuntimeException error) {
            showOffline("Termux refused the command. Enable allow-external-apps and install the controller script.");
        }
    }

    private void pollUntilReady(final int attempt) {
        if (attempt >= 20) {
            showOffline("Backend did not become ready. Open Termux and inspect the Crosstalk log.");
            return;
        }
        handler.postDelayed(new Runnable() {
            @Override public void run() {
                new Thread(new Runnable() {
                    @Override public void run() {
                        final boolean ready = backendResponds();
                        handler.post(new Runnable() {
                            @Override public void run() {
                                if (ready) {
                                    setOnline();
                                    webView.loadUrl(LOCAL_ORIGIN);
                                } else {
                                    status.setText("STARTING " + (attempt + 1) + "/20");
                                    pollUntilReady(attempt + 1);
                                }
                            }
                        });
                    }
                }, "crosstalk-start-probe").start();
            }
        }, 750L);
    }

    private void setOnline() {
        status.setText("LOCAL • ONLINE");
        offlinePanel.setVisibility(View.GONE);
        webView.setVisibility(View.VISIBLE);
    }

    private void showOffline(String message) {
        status.setText("OFFLINE");
        offlineMessage.setText(message);
        webView.setVisibility(View.GONE);
        offlinePanel.setVisibility(View.VISIBLE);
    }

    private boolean isTermuxInstalled() {
        try {
            getPackageManager().getPackageInfo(TERMUX_PACKAGE, 0);
            return true;
        } catch (PackageManager.NameNotFoundException ignored) {
            return false;
        }
    }

    private boolean hasTermuxPermission() {
        return checkSelfPermission(TERMUX_PERMISSION) == PackageManager.PERMISSION_GRANTED;
    }

    private void openTermux() {
        Intent intent = getPackageManager().getLaunchIntentForPackage(TERMUX_PACKAGE);
        if (intent == null) {
            try { startActivity(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                    Uri.parse("package:" + getPackageName()))); }
            catch (RuntimeException ignored) { toast("Termux is not installed"); }
            return;
        }
        startActivity(intent);
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(requestCode, permissions, results);
        boolean granted = results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED;
        if (requestCode == REQUEST_TERMUX) {
            if (granted) startBackend();
            else showOffline("Grant Crosstalk permission to run its fixed Termux controller command.");
        } else if (requestCode == REQUEST_AUDIO && audioPermissionRequest != null) {
            if (granted) audioPermissionRequest.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
            else audioPermissionRequest.deny();
            audioPermissionRequest = null;
        }
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != REQUEST_FILE || fileCallback == null) return;
        Uri[] result = WebChromeClient.FileChooserParams.parseResult(resultCode, data);
        fileCallback.onReceiveValue(result);
        fileCallback = null;
    }

    @Override public void onBackPressed() {
        if (webView != null && webView.getVisibility() == View.VISIBLE && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    @Override protected void onDestroy() {
        probeGeneration++;
        handler.removeCallbacksAndMessages(null);
        if (fileCallback != null) fileCallback.onReceiveValue(null);
        if (audioPermissionRequest != null) audioPermissionRequest.deny();
        if (webView != null) {
            webView.stopLoading();
            webView.destroy();
        }
        super.onDestroy();
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private void toast(String text) {
        Toast.makeText(this, text, Toast.LENGTH_SHORT).show();
    }
}
