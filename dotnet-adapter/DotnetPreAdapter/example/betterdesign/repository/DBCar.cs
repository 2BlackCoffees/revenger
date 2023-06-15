
using Examples.BetterDesign.Repository.CarExample;
using Examples.BetterDesign.Repository.CarExample.CarParts;

namespace Examples.BetterDesign.Repository.CarExample {


public class DBCar {
    DBCar() {

    }

    String[] getCarsForDriver(Driver driver) {
        return null;
    }

    void updateCar(Car car, Seats seats) {
    }

    void updateCar(Car car, Doors doors) {
    }

    void sellCarTo(Car car, Driver driver) {
    }
    Car getCar(Driver d)
    {
        return new Car();
    }
    Driver getDriver(Car c)
    {
        return new Driver();
    }
    Wheels getWheels(Car c)
    {
        return null;
    }
    Doors getDoors(Car c)
    {
        return null;
    }
    Seats getSeats(Car c)
    {
        return null;
    }
} 
}