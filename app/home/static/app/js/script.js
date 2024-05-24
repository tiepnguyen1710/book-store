// Update Cart
const tableCart = document.querySelector("[table-cart]");
console.log(tableCart);
if(tableCart) {
  const listInputQuantity = tableCart.querySelectorAll("input[name='quantity']");
  listInputQuantity.forEach(input => {
    input.addEventListener("change", () => {
      console.log(input);  
      const quantity = input.value;
      const productId = input.getAttribute("item-id");

      window.location.href = `/cart/update/${productId}/${quantity}`;
    });
  });
}

// Tìm phần tử chứa thông báo
const alertContainer = document.getElementById('alert-container');

if (alertContainer) {
    // Đặt thời gian tắt thông báo sau 3 giây
    setTimeout(function() {
        alertContainer.style.display = 'none'; // Ẩn thông báo
    }, 3000); // Thời gian tính bằng mili giây (3 giây)
}

//Pagination

const buttonPagination = document.querySelectorAll("[button-pagination]")

if(buttonPagination.length > 0){
    let url = new URL(window.location.href)

    buttonPagination.forEach(button => {
        button.addEventListener("click", (e) => {
            e.preventDefault()
            page = button.getAttribute("button-pagination");
            console.log(page)
            if(page){
                url.searchParams.set("page", page);
            }

            window.location.href = url.href;
        });
    });
}

// Sort
const sort = document.querySelector("[sort]");
if(sort) {
  let url = new URL(window.location.href);
  const sortSelect = sort.querySelector("[sort-select]");
  // Lắng nghe thay đổi sắp xếp
  sortSelect.addEventListener("change", () => {
    const [sortKey, sortValue] = sortSelect.value.split("-");

    url.searchParams.set("sortKey", sortKey);
    url.searchParams.set("sortValue", sortValue);

    window.location.href = url.href;
  });

  // Thêm selected cho lựa chọn hiện tại
  const selectedSortKey = url.searchParams.get("sortKey");
  const selectedSortValue = url.searchParams.get("sortValue");

  if(selectedSortKey && selectedSortValue) {
    const stringSort = `${selectedSortKey}-${selectedSortValue}`;
    const optionSelected = sortSelect.querySelector(`option[value='${stringSort}']`);
    optionSelected.selected = true;
  }
}
// End Sort