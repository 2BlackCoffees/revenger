package CarExample.CarParts;

public class Wheels {
    int comfort;
    int weight;
    Wheels(int comfort, int weight, int number) {
        this.comfort = comfort;
        this.weight = weight * number;
    }
    int getWeight() {
        return weight;
    }}
