package main

import (
"context"
"errors"
"fmt"

"google.golang.org/grpc/codes"
"google.golang.org/grpc/status"
)

// Simulate the current ErrorUnaryInterceptor behavior
func currentErrorHandler(err error) error {
if err == nil {
return nil
}

// given already a *status.Error then forward unchanged
if _, ok := status.FromError(err); ok {
return err
}

code := codes.Internal
// No handling for context.Canceled or context.DeadlineExceeded

return status.Error(code, err.Error())
}

// Simulate the fixed ErrorUnaryInterceptor behavior
func fixedErrorHandler(err error) error {
if err == nil {
return nil
}

// given already a *status.Error then forward unchanged
if _, ok := status.FromError(err); ok {
return err
}

// Check for context errors first
if errors.Is(err, context.Canceled) {
return status.Error(codes.Canceled, err.Error())
}
if errors.Is(err, context.DeadlineExceeded) {
return status.Error(codes.DeadlineExceeded, err.Error())
}

code := codes.Internal
return status.Error(code, err.Error())
}

func main() {
fmt.Println("Testing context error handling:")
fmt.Println("================================")

// Test context.Canceled
canceledErr := context.Canceled
currentResult := currentErrorHandler(canceledErr)
fixedResult := fixedErrorHandler(canceledErr)

currentStatus, _ := status.FromError(currentResult)
fixedStatus, _ := status.FromError(fixedResult)

fmt.Printf("\nContext Canceled:\n")
fmt.Printf("  Current handler returns: %s (expected: Internal)\n", currentStatus.Code())
fmt.Printf("  Fixed handler returns:   %s (expected: Canceled)\n", fixedStatus.Code())

// Test context.DeadlineExceeded
deadlineErr := context.DeadlineExceeded
currentResult = currentErrorHandler(deadlineErr)
fixedResult = fixedErrorHandler(deadlineErr)

currentStatus, _ = status.FromError(currentResult)
fixedStatus, _ = status.FromError(fixedResult)

fmt.Printf("\nContext DeadlineExceeded:\n")
fmt.Printf("  Current handler returns: %s (expected: Internal)\n", currentStatus.Code())
fmt.Printf("  Fixed handler returns:   %s (expected: DeadlineExceeded)\n", fixedStatus.Code())

// Test wrapped context errors (common in real applications)
wrappedCanceled := fmt.Errorf("operation failed: %w", context.Canceled)
currentResult = currentErrorHandler(wrappedCanceled)
fixedResult = fixedErrorHandler(wrappedCanceled)

currentStatus, _ = status.FromError(currentResult)
fixedStatus, _ = status.FromError(fixedResult)

fmt.Printf("\nWrapped Context Canceled:\n")
fmt.Printf("  Current handler returns: %s (expected: Internal)\n", currentStatus.Code())
fmt.Printf("  Fixed handler returns:   %s (expected: Canceled)\n", fixedStatus.Code())
}