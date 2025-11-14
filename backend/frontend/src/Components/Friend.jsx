import UserIcon from "./Element/icon/UserIcon";

const Friend = () => {
  const list = [
    {
      name: "mipan",
    },
    {
      name: "abdula",
    },
    {
      name: "Raddit",
    },
    {
      name: "Suaah",
    },
    {
      name: "Luis",
    },
    {
      name: "Krishna",
    },
    {
      name: "Oskar",
    },
    {
      name: "Juid",
    },
  ];
  return (
    <div className="px-4 flex sm:px-8 md:px-10 mt-4 overflow-x-scroll font-mono">
      <div className="flex  gap-8 sm:gap-10 flex-nowrap w-max">
        {list.map((friends) => (
          <div>
            <UserIcon classFrist={"w-15 h-15"} classSecond={"w-15 w-15"} />
            <h1 className="text-center mt-3">@{friends.name}</h1>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Friend;
