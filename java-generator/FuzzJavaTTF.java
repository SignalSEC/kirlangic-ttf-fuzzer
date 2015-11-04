import javafx.application.Application;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.layout.VBox;
import javafx.scene.text.*;
import javafx.stage.Stage;

public class FuzzJavaTTF extends Application {
  public static void main(String[] args) { launch(args); }
  @Override public void start(Stage stage) {
    stage.setTitle("KIRLANGIC TEST");

    Font.loadFont(
      FuzzJavaTTF.class.getResource("Dexter.ttf").toExternalForm(), 
      10
    );	


    Label title = new Label("Kirlangic Java Test");
    title.getStyleClass().add("title");

    Label caption = new Label("kirlangiclar acayip guzel gulerler");
    caption.getStyleClass().add("caption");
    caption.setMaxWidth(220);
    caption.setWrapText(true);
    caption.setTextAlignment(TextAlignment.CENTER);


    VBox layout = new VBox(10);
    layout.setStyle("-fx-padding: 20px; -fx-font-family: Dexter; -fx-background-color: white");
    layout.setAlignment(Pos.CENTER);
    layout.getChildren().setAll(
      title,
      caption
    );

    final Scene scene = new Scene(layout);
    stage.setScene(scene);
    stage.show();
  }
}