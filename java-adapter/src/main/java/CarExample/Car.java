package CarExample;

import CarExample.CarParts.Doors;
import CarExample.CarParts.Driver;
import CarExample.CarParts.Seats;
import CarExample.CarParts.Wheels;

class Vehicle
{
    int speed;
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
public class Car extends Driver {
    Wheels wheels;
    Vehicle vehicle;

    public Car()
    {}
    void createCar(Doors doors)
    {
        Seats seats;
    }
}
