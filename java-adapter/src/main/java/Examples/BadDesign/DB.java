package Examples.BadDesign;

import Examples.BadDesign.CarExample.Car;
import Examples.BadDesign.CarExample.CarParts.Doors;
import Examples.BadDesign.CarExample.CarParts.Driver;
import Examples.BadDesign.CarExample.CarParts.Seats;
import Examples.BadDesign.CarExample.CarParts.Wheels;
import Examples.BadDesign.FakeEntitities.Complaints;
import Examples.BadDesign.FakeEntitities.Customer;
import Examples.BadDesign.FakeEntitities.Invoice;
import Examples.BadDesign.FakeEntitities.Item;
import Examples.BadDesign.FakeEntitities.User;

public class DB {
    DB() {

    }

    String[] get(String queryString) {
        return null;
    }
    String[] getCarsWhere(String whereQueryString) {
        return null;
    }
    void set(String queryString) {
    }
    void update(String queryString) {
    }

    User getUserWhere(String query) {
        return null;
    }
    Customer getCustomerWhere(String query) {
        return null;
    }
    Item getItemWhere(String query) {
        return null;
    }
    Invoice getInvoiceWhere(String query) {
        return null;
    }
    Complaints getComplaintsWhere(String query) {
        return null;
    }
    User getUserHavingItem(Item item) {
        return null;
    }
    Customer getCustomerFromComplaint(Complaints complaint) {
        return null;
    }
    Item getItemFromUser(User user) {
        return null;
    }
    Invoice getInvoiceFromCustomer(Customer c) {
        return null;
    }
    Complaints getComplaintsFromItem(Item item) {
        return null;
    }
    User getFirstUser() {
        return null;
    }
    Customer getFirstCustomerWhere() {
        return null;
    }
    Item getFirstItem() {
        return null;
    }
    Invoice getFirstInvoice() {
        return null;
    }
    Complaints getFirstComplaints() {
        return null;
    }
    Car getCarFromDriver(Driver d)
    {
        return new Car();
    }
    Driver getDriverFromCar(Car c)
    {
        return new Driver();
    }
    Wheels getWheelsFromCar(Car c)
    {
        return null;
    }
    Doors getDoorsFromCar(Car c)
    {
        return null;
    }
    Seats getSeatsFromCar(Car c)
    {
        return null;
    }
} 