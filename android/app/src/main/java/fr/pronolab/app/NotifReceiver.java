package fr.pronolab.app;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

/** Affiche un rappel programmé par la page (match d'une équipe suivie, d'un ticket, tickets du jour). */
public class NotifReceiver extends BroadcastReceiver {
    static final String CHANNEL = "rappels";
    static final String ACTION = "fr.pronolab.NOTIF";

    @Override
    public void onReceive(Context c, Intent i) {
        NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) return;
        if (Build.VERSION.SDK_INT >= 26) {
            nm.createNotificationChannel(new NotificationChannel(CHANNEL, "Rappels de matchs", NotificationManager.IMPORTANCE_DEFAULT));
        }
        Intent open = new Intent(c, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent pi = PendingIntent.getActivity(c, 0, open, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        String title = i.getStringExtra("title"), body = i.getStringExtra("body");
        Notification.Builder b = Build.VERSION.SDK_INT >= 26 ? new Notification.Builder(c, CHANNEL) : new Notification.Builder(c);
        b.setSmallIcon(R.drawable.ic_notif)
         .setContentTitle(title == null ? "Prono Lab" : title)
         .setContentText(body == null ? "" : body)
         .setStyle(new Notification.BigTextStyle().bigText(body == null ? "" : body))
         .setAutoCancel(true)
         .setContentIntent(pi);
        try { nm.notify(i.getIntExtra("nid", 1), b.build()); } catch (SecurityException ignored) { }
    }
}
