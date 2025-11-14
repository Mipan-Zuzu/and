import UserIcon from '../Element/icon/UserIcon'

const Navbar = () => {
  return (
    <>
      <div className="flex px-10 items-center justify-between p-3 mt-2 mb-4 ">
        <h1 className="text-5xl -ml-3 font-bold xl:ml-3">and&
        </h1>
        <UserIcon classFrist={'w-10 h-10'} classSecond={'w-10 w-10'}/>
      </div>
    </>
  );
};

export default Navbar;
