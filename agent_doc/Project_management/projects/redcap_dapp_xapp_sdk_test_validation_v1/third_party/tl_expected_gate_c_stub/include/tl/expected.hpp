#ifndef REDCAP_GATE_C_TL_EXPECTED_STUB_HPP
#define REDCAP_GATE_C_TL_EXPECTED_STUB_HPP

#include <stdexcept>
#include <type_traits>
#include <utility>
#include <variant>

namespace tl {

template<typename E>
class unexpected {
public:
    explicit unexpected(const E& error) : error_(error) {}
    explicit unexpected(E&& error) : error_(std::move(error)) {}

    const E& value() const& { return error_; }
    E& value() & { return error_; }
    E&& value() && { return std::move(error_); }

private:
    E error_;
};

template<typename T, typename E>
class expected {
public:
    expected(const T& value) : storage_(value) {}
    expected(T&& value) : storage_(std::move(value)) {}
    expected(const unexpected<E>& error) : storage_(error.value()) {}
    expected(unexpected<E>&& error) : storage_(std::move(error).value()) {}

    bool has_value() const noexcept { return std::holds_alternative<T>(storage_); }
    explicit operator bool() const noexcept { return has_value(); }

    T& value() &
    {
        if (!has_value()) {
            throw std::logic_error("tl::expected has no value");
        }
        return std::get<T>(storage_);
    }

    const T& value() const&
    {
        if (!has_value()) {
            throw std::logic_error("tl::expected has no value");
        }
        return std::get<T>(storage_);
    }

    T&& value() &&
    {
        if (!has_value()) {
            throw std::logic_error("tl::expected has no value");
        }
        return std::move(std::get<T>(storage_));
    }

    E& error() &
    {
        return std::get<E>(storage_);
    }

    const E& error() const&
    {
        return std::get<E>(storage_);
    }

    T& operator*() & { return value(); }
    const T& operator*() const& { return value(); }
    T* operator->() { return &value(); }
    const T* operator->() const { return &value(); }

private:
    std::variant<T, E> storage_;
};

} // namespace tl

#endif // REDCAP_GATE_C_TL_EXPECTED_STUB_HPP
