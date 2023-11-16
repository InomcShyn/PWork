package com.example.pwork.view.vation;
import android.app.DatePickerDialog;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.example.pwork.R;
import com.example.pwork.database.HikeDatabase;
import com.example.pwork.model.Obser;
import java.util.Calendar;

public class ObserAdd extends AppCompatActivity {

    private EditText observationEditText, timeOfObservationEditText, commentsEditText;
    private ImageButton customButton;
    private Button addObservationButton;
    private HikeDatabase db;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_obser_add);

        db = HikeDatabase.getDatabase(getApplicationContext());

        observationEditText = findViewById(R.id.observationEditText);
        timeOfObservationEditText = findViewById(R.id.timeOfObservationEditText);
        commentsEditText = findViewById(R.id.commentsEditText);
        addObservationButton = findViewById(R.id.addObservationButton);

        customButton = findViewById(R.id.custom_button);
        customButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                finish(); // Kết thúc EditHike và quay lại DetailsHike
            }
        });

        timeOfObservationEditText.setOnClickListener(v -> showDatePickerDialog());

        addObservationButton.setOnClickListener(v -> {
            String observation = observationEditText.getText().toString().trim();
            String timeOfObservation = timeOfObservationEditText.getText().toString().trim();
            String comments = commentsEditText.getText().toString().trim();

            if (!validateInput(observation, timeOfObservation)) {
                Toast.makeText(this, "Invalid input provided", Toast.LENGTH_SHORT).show();
                return;
            }

            Obser newObser = new Obser();
            newObser.observation = observation;
            newObser.timeOfObservation = timeOfObservation;
            newObser.comments = comments;

            new Thread(() -> {
                db.observationDao().insert(newObser);
                // Send a broadcast to notify Observations activity of the new observation
                sendBroadcast(new Intent("observation_added"));
                runOnUiThread(() -> {
                    Toast.makeText(getApplicationContext(), "Observation successfully added", Toast.LENGTH_SHORT).show();
                    finish(); // Close the activity after adding the new observation
                });
            }).start();
        });
    }

    private void showDatePickerDialog() {
        Calendar calendar = Calendar.getInstance();
        DatePickerDialog datePickerDialog = new DatePickerDialog(
                this,
                (view, year, monthOfYear, dayOfMonth) -> {
                    String selectedDate = String.format("%02d/%02d/%04d", dayOfMonth, monthOfYear + 1, year);
                    timeOfObservationEditText.setText(selectedDate);
                },
                calendar.get(Calendar.YEAR),
                calendar.get(Calendar.MONTH),
                calendar.get(Calendar.DAY_OF_MONTH)
        );

        datePickerDialog.show();
    }

    private boolean validateInput(String observation, String timeOfObservation) {
        // Check if observation or timeOfObservation is empty
        return !observation.isEmpty() && !timeOfObservation.isEmpty();
    }
}
