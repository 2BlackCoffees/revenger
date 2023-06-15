
using Examples.BadDesign;
using Examples.BadDesign.CarExample.CarParts;

namespace Examples.BadDesign.CarExample {

class Vehicle
{
    int speed;
    DB db;
    public Vehicle()
    {

    }
    void setSpeed(int speed) {
        this.speed = speed;
    }
    int getSpeed() {
        return speed;
    }
}
public class Car : Driver {
    Wheels wheels;
    Vehicle vehicle;
    DB db;

    public Car()
    {}
    void createCar(Doors doors)
    {
        Seats seats;
    }
}
}