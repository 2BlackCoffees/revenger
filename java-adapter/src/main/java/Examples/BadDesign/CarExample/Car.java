package Examples.BadDesign.CarExample;

import Examples.BadDesign.DB;
import Examples.BadDesign.CarExample.CarParts.Doors;
import Examples.BadDesign.CarExample.CarParts.Driver;
import Examples.BadDesign.CarExample.CarParts.Seats;
import Examples.BadDesign.CarExample.CarParts.Wheels;

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
public class Car extends Driver {
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
